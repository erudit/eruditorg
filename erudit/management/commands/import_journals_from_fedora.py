# -*- coding: utf-8 -*-
import itertools
import datetime as dt
import logging
import re
import urllib.parse

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q
from django.template.defaultfilters import slugify
from django.utils.encoding import smart_str
from eruditarticle.objects import EruditArticle
from eruditarticle.utils import remove_xml_namespaces
import lxml.etree as et

from ...conf import settings as erudit_settings
from ...fedora.objects import ArticleDigitalObject
from ...fedora.objects import JournalDigitalObject
from ...fedora.objects import PublicationDigitalObject
from ...fedora.utils import get_pids
from ...fedora.utils import is_issue_published_in_fedora
from ...fedora.utils import get_unimported_issues_pids
from ...fedora.repository import api
from ...models import Affiliation
from ...models import Article
from ...models import ArticleTitle
from ...models import ArticleSubtitle
from ...models import ArticleAbstract
from ...models import ArticleSectionTitle
from ...models import Author
from ...models import Collection
from ...models import Copyright
from ...models import Issue
from ...models import IssueTheme
from ...models import IssueContributor
from ...models import Journal
from ...models import KeywordTag
from ...models import Publisher

logger = logging.getLogger(__name__)


def _create_issue_contributor_object(issue_contributor, issue, is_director=False, is_editor=False):
    contributor = IssueContributor(
        firstname=issue_contributor['firstname'],
        lastname=issue_contributor['lastname'],
        issue=issue
    )

    if is_director:
        contributor.is_director = True
    if is_editor:
        contributor.is_editor = True
    contributor_roles = issue_contributor.get('role')
    if contributor_roles:
        role_fr = contributor_roles.get('fr')
        role_en = contributor_roles.get('en')

        if role_fr and role_en:
            raise ValueError('Only one of role_fr or role_en should be defined')
        if role_fr:
            contributor.role_name = role_fr
        if role_en:
            contributor.role_name = role_en
        if not role_fr and not role_en:
            if len(contributor_roles.keys()) > 0:
                _, contributor.role_name = contributor_roles.popitem()
    return contributor


class Command(BaseCommand):
    """ Imports journal objects from a Fedora Commons repository.

    The command is able to import a journal object - including its issues and its articles - from
    a Fedora Commons repository. To do so, the command assumes that some journal collections
    (:py:class`Collection <erudit.models.core.Collection>` instances) are already created in the
    database.

    By default the command will try to import the journal objects that have been modified since the
    latest journal modification date stored in the database. If no journals can be found in the
    database, the command will perform a full import.
    """

    help = 'Import journals from Fedora'

    def add_arguments(self, parser):
        parser.add_argument(
            '--full', action='store_true', dest='full', default=False,
            help='Perform a full import.')

        parser.add_argument(
            '--test-xslt', action='store', dest='test_xslt',
            help='Python path to a function to test the XSLT transformation of articles')

        parser.add_argument(
            '--make-published', action='store_true', dest='make_published', default=False,
            help='Determines if the issues should be considered published (default: false)')

        parser.add_argument(
            '--pid', action='store', dest='journal_pid', help='Journal PID to manually import.')

        parser.add_argument(
            '--issue-pid', action='store', dest='issue_pid', help='Issue PID to manually import.')  # noqa

        parser.add_argument(
            '--import-missing', action='store_true', dest='import_missing', help='Import missing issues.'  # noqa
        )
        parser.add_argument(
            '--mdate', action='store', dest='mdate',
            help='Modification date to use to retrieve journals to import (iso format).')

    def handle(self, *args, **options):
        self.full_import = options.get('full', False)
        self.test_xslt = options.get('test_xslt', None)
        self.make_published = options.get('make_published', False)
        self.journal_pid = options.get('journal_pid', None)
        self.modification_date = options.get('mdate', None)
        self.journal_precendence_relations = []
        self.issue_pid = options.get('issue_pid', None)
        self.import_missing = options.get('import_missing', None)
        logger.info("=" * 10 + "Import started" + "=" * 10)
        logger.info("options: {}".format(options))

        # Handles a potential XSLT test function
        try:
            assert self.test_xslt is not None
            module, xslt_test_func = self.test_xslt.rsplit('.', 1)
            module, xslt_test_func = smart_str(module), smart_str(xslt_test_func)
            xslt_test_func = getattr(__import__(module, {}, {}, [xslt_test_func]), xslt_test_func)
            self.xslt_test_func = xslt_test_func
        except ImportError:
            self.stdout.write(self.style.ERROR(
                '"{0}" could not be imported!'.format(self.test_xslt)))
            return
        except AssertionError:
            pass

        # Handles a potential modification date option
        try:
            assert self.modification_date is not None
            self.modification_date = dt.datetime.strptime(self.modification_date, '%Y-%m-%d').date()
        except ValueError:
            self.stdout.write(self.style.ERROR(
                '"{0}" is not a valid modification date!'.format(self.modification_date)))

            return
        except AssertionError:
            pass

        if self.issue_pid or self.import_missing:
            if self.issue_pid:
                self.stdout.write(self.style.MIGRATE_HEADING(
                    'Start importing issue with PID: {0}'.format(self.issue_pid)))
                if not re.match(r'^\w+\:\w+\.\w+\.\w+$', self.issue_pid):
                    self.stdout.write(self.style.ERROR(
                        '  "{0}" is not a valid journal PID!'.format(self.issue_pid)))
            else:
                self.stdout.write(self.style.MIGRATE_HEADING(
                    'Start importing missing issues.'
                ))

            if self.issue_pid:
                unimported_issues_pids = [self.issue_pid]
            else:
                unimported_issues_pids = get_unimported_issues_pids()
                self.stdout.write("{} issues to import.".format(len(unimported_issues_pids)))
            for issue_pid in unimported_issues_pids:
                journal_localidentifier = issue_pid.split(':')[1].split('.')[1]
                try:
                    journal = Journal.objects.get(localidentifier=journal_localidentifier)
                except Journal.DoesNotExist:
                    self.stdout.write(self.style.ERROR(
                        'The "{0}" journal is not available.'.format(journal_localidentifier)))
                    return
                try:
                    self._import_issue(issue_pid, journal)
                except:
                    self.stdout.write(self.style.ERROR("Cannot import issue with pid {}".format(issue_pid)))
            return

            # Imports a journal PID manually
        if self.journal_pid:
            self.stdout.write(self.style.MIGRATE_HEADING(
                'Start importing journal with PID: {0}'.format(self.journal_pid)))

            if not re.match(r'^\w+\:\w+\.\w+$', self.journal_pid):
                self.stdout.write(self.style.ERROR(
                    '  "{0}" is not a valid journal PID!'.format(self.journal_pid)))
                return

            collection_localidentifier = self.journal_pid.split(':')[1].split('.')[0]
            try:
                collection = Collection.objects.get(localidentifier=collection_localidentifier)
            except Collection.DoesNotExist:
                self.stdout.write(self.style.ERROR(
                    'The "{0}" collection is not available.'.format(collection_localidentifier)))
                return

            self.import_journal(self.journal_pid, collection)
            self.import_journal_precedences(self.journal_precendence_relations)
            return

        # Imports each collection
        journal_count, journal_errored_count = 0, 0
        issue_count, issue_errored_count, article_count = 0, 0, 0
        for collection_config in erudit_settings.JOURNAL_PROVIDERS.get('fedora'):
            collection_code = collection_config.get('collection_code')
            try:
                collection = Collection.objects.get(code=collection_code)
            except Collection.DoesNotExist:
                collection = Collection.objects.create(
                    code=collection_code, name=collection_config.get('collection_title'),
                    localidentifier=collection_config.get('localidentifier'))
            else:
                _jc, _jec, _ic, _iec, _ac = self.import_collection(collection)
                journal_count += _jc
                journal_errored_count += _jec
                issue_count += _ic
                issue_errored_count += _iec
                article_count += _ac

        self.stdout.write(self.style.MIGRATE_HEADING(
            '\nJournals imported: {journal_count} / Journals errored: {journal_errored_count} / '
            'issues imported: {issue_count} / issues errored: {issue_errored_count} / '
            'articles imported: {article_count}'.format(
                journal_count=journal_count, journal_errored_count=journal_errored_count,
                issue_count=issue_count, issue_errored_count=issue_errored_count,
                article_count=article_count,
            )))

    def import_collection(self, collection):
        """ Imports all the journals of a specific collection. """
        self.stdout.write(self.style.MIGRATE_HEADING(
            'Start importing "{}" collection'.format(collection.code)))

        self.journal_precendence_relations = []

        latest_update_date = self.modification_date
        if not self.full_import and latest_update_date is None:
            # Tries to fetch the date of the Journal instance with the more recent update date.
            latest_journal_update = Journal.objects.order_by('-fedora_updated').first()
            latest_update_date = latest_journal_update.fedora_updated.date() \
                if latest_journal_update else None

        latest_issue_update_date = self.modification_date
        if not self.full_import and latest_issue_update_date is None:
            # Tries to fetch the date of the Issue instance with the more recent update date.
            latest_issue_update = Issue.objects.order_by('-fedora_updated').first()
            latest_issue_update_date = latest_issue_update.fedora_updated.date() \
                if latest_issue_update else None

        # STEP 1: fetches the PIDs of the journals that will be imported
        # --

        base_fedora_query = "pid~erudit:{collectionid}.* label='Series Erudit'".format(
            collectionid=collection.localidentifier)
        if self.full_import or latest_update_date is None:
            if not self.full_import:
                self.stdout.write(self.style.WARNING(
                    '  No journals found... proceed to full import!'.format(collection.code)))
            journal_pids = get_pids(base_fedora_query)
        else:
            self.stdout.write(
                '  Importing Journals modified since {}.'.format(latest_update_date.isoformat()))
            # Fetches the PIDs of all the journals that have been update since the latest
            # modification date.
            journal_pids = get_pids(
                base_fedora_query + ' mdate>{}'.format(latest_update_date.isoformat()))

        # STEP 2: import each journal using its PID
        # --

        journal_count, journal_errored_count = 0, 0
        for jpid in journal_pids:
            try:
                self.import_journal(jpid, collection, False)
            except Exception as e:
                journal_errored_count += 1
                self.stdout.write(self.style.ERROR(
                    '    Unable to import the journal with PID "{0}": {1}'.format(jpid, e)))
            else:
                journal_count += 1

        # STEP 3: associates Journal instances with other each other
        # --

        self.import_journal_precedences(self.journal_precendence_relations)

        # STEP 4: fetches the PIDs of the issues that will be imported
        # --
        issue_fedora_query = "pid~erudit:{collectionid}.*.* label='Publication Erudit'".format(
            collectionid=collection.localidentifier)
        if self.full_import or latest_update_date is None:
            if not self.full_import:
                self.stdout.write(self.style.WARNING(
                    '  No issues found... proceed to full import!'.format(collection.code)))
            issue_pids = get_pids(issue_fedora_query)
        else:
            self.stdout.write(
                '  Importing Issues modified since {}.'.format(latest_update_date.isoformat()))
            # Fetches the PIDs of all the issues that have been update since the latest
            # modification date.
            issue_pids = get_pids(
                issue_fedora_query + ' mdate>{}'.format(latest_issue_update_date.isoformat()))

        # STEP 5: import each issue using its PID
        # --

        issue_count, issue_errored_count, article_count = 0, 0, 0

        for ipid in issue_pids:
            try:
                journal_localidentifier = ipid.split(':')[1].split('.')[1]
                journal = Journal.objects.get(localidentifier=journal_localidentifier)
            except Journal.DoesNotExist:
                issue_errored_count += 1
                self.stdout.write(self.style.ERROR(
                    '      Failure importing issue {0}. The "{0}" journal is not available.'.format(
                        ipid, journal_localidentifier)))
            else:
                try:
                    _ac = self._import_issue(ipid, journal)
                except Exception as e:
                    issue_errored_count += 1
                    self.stdout.write(self.style.ERROR(
                        '    Unable to import the issue with PID "{0}": {1}'.format(ipid, e)))
                else:
                    issue_count += 1
                    article_count += _ac

        return journal_count, journal_errored_count, issue_count, issue_errored_count, article_count

    def import_journal_precedences(self, precendences_relations):
        """ Associates previous/next Journal instances with each journal. """
        for r in precendences_relations:
            localid = r['journal_localid']
            previous_localid = r['previous_localid']
            next_localid = r['next_localid']
            if previous_localid is None and next_localid is None:
                continue
            try:
                j = Journal.objects.get(localidentifier=localid)
                previous_journal = Journal.objects.get(localidentifier=previous_localid) \
                    if previous_localid else None
                next_journal = Journal.objects.get(localidentifier=next_localid) \
                    if next_localid else None
            except Journal.DoesNotExist:
                self.stdout.write(self.style.ERROR(
                    '    Unable to import the precedences for journal with '
                    'localidentifier "{0}"'.format(localid)))
            else:
                j.previous_journal = previous_journal
                j.next_journal = next_journal
                j.save()

    @transaction.atomic
    def import_journal(self, journal_pid, collection, import_issues=True):
        """ Imports a journal using its PID. """
        logger.info("Importing journal: {}".format(journal_pid))
        self.stdout.write(self.style.MIGRATE_LABEL(
            '    Start importing journal with PID: {0}'.format(journal_pid)))

        # STEP 1: fetches the full Journal fedora object
        # --

        try:
            fedora_journal = JournalDigitalObject(api, journal_pid)
            assert fedora_journal.exists
        except AssertionError:
            msg = 'The journal with PID "{}" seems to be inexistant'.format(journal_pid)
            logger.error(msg, exc_info=True)
            self.stdout.write('    ' + self.style.ERROR(msg))
            return  # We return here in order to try to import the other journals of the collection

        # STEP 2: creates or updates the journal object
        # --

        oaiset_info_tree = remove_xml_namespaces(
            et.fromstring(fedora_journal.oaiset_info.content.serialize())) \
            if fedora_journal.oaiset_info.exists else None
        rels_ext_tree = remove_xml_namespaces(
            et.fromstring(fedora_journal.rels_ext.content.serialize())) \
            if fedora_journal.rels_ext.exists else None
        publications_tree = remove_xml_namespaces(
            et.fromstring(fedora_journal.publications.content.serialize()))
        # Set the proper values on the Journal instance
        xml_name = oaiset_info_tree.find('.//title') if oaiset_info_tree \
            else rels_ext_tree.find('.//setName')

        # Fetches the Journal instance... or creates a new one
        journal_localidentifier = journal_pid.split('.')[-1]
        try:
            journal = Journal.objects.get(localidentifier=journal_localidentifier)
        except Journal.DoesNotExist:
            journal = Journal()
            journal.localidentifier = journal_localidentifier
            journal.collection = collection
            journal.fedora_created = fedora_journal.created
            journal.name = xml_name.text if xml_name is not None else None

        xml_issue = publications_tree.xpath(
            './/numero[starts-with(@pid, "{0}")]'.format(journal_pid))
        journal.first_publication_year = journal.erudit_object.first_publication_year
        journal.last_publication_year = journal.erudit_object.last_publication_year

        # Some journals share the same code in the Fedora repository so we have to ensure that our
        # journal instances' codes are not duplicated!
        if not journal.id:
            code_base = xml_issue[0].get('revAbr') if xml_issue is not None else None
            code_base = code_base if code_base else re.sub(r'\d', '', journal_localidentifier)
            code_ext = 1
            journal.code = code_base
            while Journal.objects.filter(code=journal.code).exists():
                journal.code = code_base + str(code_ext)
                code_ext += 1

        issues = xml_issue = publications_tree.xpath('.//numero')
        current_journal_localid_found = False
        precendences_relation = {
            'journal_localid': journal.localidentifier,
            'previous_localid': None,
            'next_localid': None,
        }
        for issue in issues:
            issue_pid = issue.get('pid')
            journal_localid = issue_pid.split('.')[-2]
            if journal_localid != journal.localidentifier and not current_journal_localid_found:
                precendences_relation['next_localid'] = journal_localid
            elif journal_localid != journal.localidentifier and current_journal_localid_found:
                precendences_relation['previous_localid'] = journal_localid
            elif journal_localid == journal.localidentifier:
                current_journal_localid_found = True
        self.journal_precendence_relations.append(precendences_relation)

        journal_created = journal.id is None

        journal.fedora_updated = fedora_journal.modified
        journal.save()

        # Associates the publisher to the Journal instance
        xml_publisher = oaiset_info_tree.find('.//publisher') if oaiset_info_tree else None
        publisher_name = xml_publisher.text if xml_publisher is not None else None
        if publisher_name is not None:
            publisher, _ = Publisher.objects.get_or_create(name=publisher_name)
            journal.publishers.add(publisher)
        else:
            logger.error(
                'The journal with PID "{}" has been created or updated '
                'without publisher'.format(journal_pid), exc_info=True)

        if journal_created:
            self.stdout.write('      Journal instance created: "{}"'.format(journal.name))
        else:
            self.stdout.write('      Journal instance updated: "{}"'.format(journal.name))

        # STEP 3: imports all the issues associated with the journal
        # --
        if import_issues is False:
            return 0, 0

        issue_count, article_count = 0, 0

        issue_fedora_query = "pid~erudit:{collectionid}.{journalid}.* label='Publication Erudit'"
        issue_fedora_query = issue_fedora_query.format(
            collectionid=journal.collection.localidentifier,
            journalid=journal.localidentifier
        )
        issue_pids = get_pids(issue_fedora_query)
        for ipid in issue_pids:
            if ipid.startswith(journal_pid):
                # Imports the issue only if its PID is prefixed with the PID of the journal object.
                # In any other case this means that the issue is associated with another journal and
                # it will be imported later.
                _ac = self._import_issue(ipid, journal)
                issue_count += 1
                article_count += _ac

        return issue_count, article_count

    def _import_issue(self, issue_pid, journal):
        """ Imports an issue using its PID. """
        self.stdout.write('      Importing issue with PID "{0}"...'.format(issue_pid), ending='')

        # STEP 1: fetches the full Issue fedora object
        # --

        try:
            fedora_issue = PublicationDigitalObject(api, issue_pid)
            assert fedora_issue.exists
        except AssertionError:
            self.stdout.write(self.style.ERROR('  [FAIL]'))
            logger.error(
                'The issue with PID "{}" seems to be inexistant'.format(issue_pid), exc_info=True)
            raise

        # STEP 2: creates or updates the issue object
        # --

        # Fetches the Issue instance... or creates a new one
        issue_localidentifier = issue_pid.split('.')[-1]
        try:
            issue = Issue.objects.get(localidentifier=issue_localidentifier)
        except Issue.DoesNotExist:
            issue = Issue()
            issue.localidentifier = issue_localidentifier
            issue.journal = journal
            issue.fedora_created = fedora_issue.created

        summary_tree = remove_xml_namespaces(
            et.fromstring(fedora_issue.summary.content.serialize()))

        # Set the proper values on the Issue instance
        issue.year = issue.erudit_object.publication_year
        issue.publication_period = issue.erudit_object.publication_period
        issue.volume = issue.erudit_object.volume
        issue.number = issue.erudit_object.number
        issue.first_page = issue.erudit_object.first_page
        issue.last_page = issue.erudit_object.last_page
        issue.title = issue.erudit_object.theme
        issue.html_title = issue.erudit_object.html_theme
        issue.thematic_issue = issue.erudit_object.theme is not None
        issue.date_published = issue.erudit_object.publication_date \
            or dt.datetime(int(issue.year), 1, 1)
        issue.date_produced = issue.erudit_object.production_date \
            or issue.erudit_object.publication_date

        # Is the Issue published ?
        issue.is_published = is_issue_published_in_fedora(issue_pid, journal=journal)

        issue.fedora_updated = fedora_issue.modified
        issue.save()
        logger.info("Issue imported: {}".format(issue.localidentifier))
        issue.contributors.all().delete()

        for director in issue.erudit_object.directors:
            contributor = _create_issue_contributor_object(
                director,
                issue,
                is_director=True
            )
            contributor.save()

        for editor in issue.erudit_object.editors:
            contributor = _create_issue_contributor_object(
                editor,
                issue,
                is_editor=True
            )
            contributor.save()

        issue.copyrights.clear()
        copyrights_dicts = issue.erudit_object.droitsauteur or []
        for copyright_dict in copyrights_dicts:
            copyright_text = copyright_dict.get('text', None)
            copyright_url = copyright_dict.get('url', None)
            if copyright_text is None:
                continue
            copyright, _ = Copyright.objects.get_or_create(text=copyright_text, url=copyright_url)
            issue.copyrights.add(copyright)

        # STEP 3: impors all the themes associated with the considered issue
        # --

        issue.themes.all().delete()
        for theme_id, theme_dict in issue.erudit_object.themes.items():
            issue_theme = IssueTheme(issue=issue, identifier=theme_id, paral=False)
            issue_theme.name = theme_dict.get('name')
            issue_theme.subname = theme_dict.get('subname')
            issue_theme.html_name = theme_dict.get('html_name')
            issue_theme.html_subname = theme_dict.get('html_subname')

            if not issue_theme.name:
                continue

            issue_theme.save()
            for theme_paral_id, theme_paral_dict in theme_dict.get('paral').items():
                issue_theme_paral = IssueTheme(issue=issue, identifier=theme_id, paral=True)
                issue_theme_paral.name = theme_paral_dict.get('name')
                issue_theme_paral.subname = theme_paral_dict.get('subname')
                issue_theme_paral.html_name = theme_paral_dict.get('html_name')
                issue_theme_paral.html_subname = theme_paral_dict.get('html_subname')
                issue_theme_paral.save()

        # STEP 4: patches the journal associated with the issue
        # --

        # Journal name
        self._patch_generic_journal_title(journal, 'name', issue.erudit_object.journal_titles or {})
        if not journal.subtitle:
            self._patch_generic_journal_title(
                journal, 'subtitle', issue.erudit_object.journal_subtitles or {})
        journal.issn_print = issue.erudit_object.issn
        journal.issn_web = issue.erudit_object.issn_num
        journal.save()

        # STEP 5: imports all the articles associated with the issue
        # --

        article_count = 0

        xml_article_nodes = summary_tree.findall('.//article')
        for article_node in xml_article_nodes:
            try:
                apid = issue_pid + '.{0}'.format(article_node.get('idproprio'))
                self._import_article(apid, article_node, issue)
            except Exception as e:
                self.stdout.write(self.style.ERROR('  [FAIL]'))
                logger.error(
                    'The issue\'s article with PID "{0}" cannot be imported: {1}'.format(apid, e),
                    exc_info=True)
                raise
            else:
                article_count += 1

        self.stdout.write(self.style.SUCCESS('  [OK]'))

        return article_count

    def _import_article(self, article_pid, issue_article_node, issue):
        """ Imports an article using its PID. """

        # STEP 1: fetches the full Article fedora object
        # --

        try:
            fedora_article = ArticleDigitalObject(api, article_pid)
            assert fedora_article.exists
        except AssertionError:
            # FIXME handle this more elegantly
            #
            # A hack has been used to implement continuous publication for ageo.
            # The consequence of this hack is that issue summaries reference articles that do not
            # exist in Fedora. To bypass this, we silently ignore non-existent articles for ageo.
            #
            # ref https://redmine.erudit.team/issues/2296
            if "ageo1499289" in article_pid:
                logger.warn(
                    'The ageo1499289 article with PID "{}" has been SKIPPED'.format(article_pid)
                )
                return
            else:
                logger.error(
                    'The article with PID "{}" seems to be inexistant'.format(article_pid),
                    exc_info=True)
                raise

        # STEP 2: creates or updates the article object
        # --

        # Fetches the Article instance... or creates a new one
        article_localidentifier = article_pid.split('.')[-1]
        try:
            article = Article.objects.get(localidentifier=article_localidentifier)
        except Article.DoesNotExist:
            article = Article()
            article.localidentifier = article_localidentifier
            article.issue = issue
            article.fedora_created = fedora_article.created

        article.fedora_updated = fedora_article.modified

        urlnode = issue_article_node.find('.//urlhtml')
        urlnode = issue_article_node.find('.//urlpdf') if urlnode is None else urlnode
        is_external_article = False
        if urlnode is not None:
            urlnode_parsed = urllib.parse.urlparse(urlnode.text)
            is_external_article = len(urlnode_parsed.netloc) and \
                'erudit.org' not in urlnode_parsed.netloc

        if is_external_article:
            self._import_article_from_issue_node(article, issue_article_node)
        elif fedora_article.erudit_xsd300.exists:
            self._import_article_from_eruditarticle_v3(article, issue_article_node)

    def _import_article_from_issue_node(self, article, issue_article_node):
        """ Imports an article using its definition in the issue's summary. """
        xml = et.tostring(issue_article_node)
        erudit_object = EruditArticle(xml)
        self._import_article_from_eruditarticle_v3(
            article,
            issue_article_node,
            article_erudit_object=erudit_object
        )

        urlhtml = issue_article_node.find('.//urlhtml')
        urlpdf = issue_article_node.find('.//urlpdf')
        article.external_url = urlhtml.text if urlhtml is not None else urlpdf.text
        if urlpdf is not None:
            article.external_pdf_url = urlpdf.text
        article.save()

    def _get_is_publication_allowed(self, issue_article_node):
        """ Return True if the publication of this article is allowed """
        accessible = issue_article_node.find('accessible')
        if accessible is not None and accessible.text == 'non':
            return False
        return True

    def _import_article_from_eruditarticle_v3(
        self, article, issue_article_node, article_erudit_object=None
    ):
        """ Imports an article using the EruditArticle v3 specification. """
        article_erudit_object = article_erudit_object or article.erudit_object

        # Set the proper values on the Article instance
        processing = article_erudit_object.processing
        processing_mapping = {'minimal': 'M', 'complet': 'C', '': 'M', }
        try:
            article.processing = processing_mapping[processing]
        except KeyError:
            raise ValueError(
                'Unable to determine the processing type of the article '
                'with PID {0}'.format(article.pid))

        article.type = article_erudit_object.article_type
        article.ordseq = int(article_erudit_object.ordseq)
        article.doi = article_erudit_object.doi
        article.first_page = article_erudit_object.first_page
        article.last_page = article_erudit_object.last_page
        article.subtitle = article_erudit_object.subtitle

        surtitle = article_erudit_object.get_section_titles(level=1)
        if surtitle:
            article.surtitle = surtitle['main']
        article.language = article_erudit_object.language
        article.publication_allowed = self._get_is_publication_allowed(issue_article_node)
        article.formatted_title = article_erudit_object.get_formatted_title()
        article.clean()
        article.save()

        titles = article_erudit_object.get_titles()

        # Delete all the titles of the article
        ArticleTitle.objects.filter(article=article).delete()
        ArticleSubtitle.objects.filter(article=article).delete()

        # Reimport titles
        ArticleTitle(
            article=article, paral=False, title=titles['main'].title,
        ).save()

        if titles['main'].subtitle:
            ArticleSubtitle(article=article, paral=False, title=titles['main'].subtitle)

        for paral_title in itertools.chain(titles['paral'], titles['equivalent']):
            ArticleTitle(
                article=article,
                language=paral_title.lang,
                title=paral_title.title,
                paral=True
            ).save()

            if paral_title.subtitle:
                ArticleSubtitle(
                    article=article,
                    language=paral_title.lang,
                    title=paral_title.subtitle,
                    paral=True
                ).save()

        # STEP 3: creates or updates the authors of the article
        # --

        article.authors.clear()
        for author_xml in article_erudit_object.findall('liminaire//grauteur//auteur'):
            firstname_xml = author_xml.find('.//nompers/prenom')
            firstname = firstname_xml.text if firstname_xml is not None else None
            lastname_xml = author_xml.find('.//nompers/nomfamille')
            lastname = lastname_xml.text if lastname_xml is not None else None
            suffix_xml = author_xml.find('.//nompers/suffixe')
            suffix = suffix_xml.text if suffix_xml is not None else None
            organization_xml = author_xml.find('.//nomorg')
            organization = organization_xml.text if organization_xml is not None else None
            affiliations = [
                affiliation_dom.text
                for affiliation_dom in author_xml.findall('.//affiliation/alinea')]

            if firstname is None and lastname is None and organization is None:
                continue

            author_query_kwargs = {
                'firstname': firstname, 'lastname': lastname, 'othername': organization}

            author = Author.objects.filter(**author_query_kwargs).first()
            if author is None:
                author = Author(**author_query_kwargs)
            author.suffix = suffix
            author.save()

            author.affiliations.clear()
            for aff in affiliations:
                if not aff:
                    continue
                affiliation, _ = Affiliation.objects.get_or_create(name=aff)
                author.affiliations.add(affiliation)

            article.authors.add(author)

        # STEP 4: imports the abstracts associated with the article
        # --

        article.abstracts.all().delete()
        for abstract_dict in article_erudit_object.abstracts:
            abstract = ArticleAbstract(article=article)
            abstract.text = abstract_dict.get('content')
            abstract.language = abstract_dict.get('lang')
            abstract.save()

        # STEP 5: imports the section titles associated with the article
        # --

        article.section_titles.all().delete()
        for level in range(1, 4):
            section_titles_dict = article_erudit_object.get_section_titles(level=level)
            if section_titles_dict is None:
                continue

            section_title = ArticleSectionTitle(article=article, level=level, paral=False)
            section_title.title = section_titles_dict.get('main')
            section_title.save()

            for paral in section_titles_dict.get('paral').values():
                section_title_paral = ArticleSectionTitle(article=article, level=level, paral=True)
                section_title_paral.title = paral
                section_title_paral.save()

        # STEP 6: imports the article's keywords
        # --

        article.keywords.clear()
        for keywords_dict in article_erudit_object.keywords:
            lang = keywords_dict.get('lang')
            for kword in keywords_dict.get('keywords', []):
                if not kword:
                    continue

                try:
                    tag = KeywordTag.objects.filter(
                        Q(slug=slugify(kword)[:100]) | Q(name=kword[:100])).first()
                    assert tag is not None
                except AssertionError:
                    tag = KeywordTag.objects.create(
                        name=kword, slug=slugify(kword)[:100], language=lang)
                else:
                    tag.language = lang
                    tag.save()
                article.keywords.add(tag)

        # STEP 7: imports article's copyrights
        # --

        article.copyrights.clear()
        copyrights_dicts = article_erudit_object.droitsauteur or []
        for copyright_dict in copyrights_dicts:
            copyright_text = copyright_dict.get('text', None)
            copyright_url = copyright_dict.get('url', None)
            if copyright_text is None:
                continue
            copyright, _ = Copyright.objects.get_or_create(text=copyright_text, url=copyright_url)
            article.copyrights.add(copyright)

        # STEP 8: eventually test the XSLT transformation of the article
        # --

        if self.test_xslt:
            try:
                self.xslt_test_func({}, article)
            except Exception as e:
                msg = 'The article with PID "{}" cannot be rendered using XSLT: e'.format(
                    article.pid, e)
                self.stdout.write(self.style.ERROR('      ' + msg))
                logger.error(msg, exc_info=True)

    def _patch_generic_journal_title(self, journal, field_name, titles):
        assigned_langs = []
        for lang, name in titles.get('paral', {}).items():
            try:
                title_attr = '{0}_{1}'.format(field_name, lang)
                assert hasattr(journal, title_attr)
                setattr(journal, title_attr, name)
            except AssertionError:  # pragma no cover
                # Unsupported language?
                pass
            else:
                assigned_langs.append(lang)
        unassigned_langs = list(
            set([l[0] for l in settings.LANGUAGES]).intersection(assigned_langs))
        try:
            main_lang = 'fr' if 'fr' not in assigned_langs else unassigned_langs[0]
            setattr(journal, '{0}_{1}'.format(field_name, main_lang), titles.get('main'))
        except KeyError:  # pragma no cover
            pass
