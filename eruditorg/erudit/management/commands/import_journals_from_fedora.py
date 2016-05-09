# -*- coding: utf-8 -*-

import datetime as dt
import logging
import re

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from eruditarticle.utils import remove_xml_namespaces
from eulfedora.util import RequestFailed
import lxml.etree as et

from apps.public.journal.templatetags.public_journal_tags import render_article

from ...conf import settings as erudit_settings
from ...fedora.objects import ArticleDigitalObject
from ...fedora.objects import JournalDigitalObject
from ...fedora.objects import PublicationDigitalObject
from ...fedora.repository import api
from ...fedora.repository import rest_api
from ...models import Article
from ...models import Author
from ...models import Collection
from ...models import Issue
from ...models import Journal
from ...models import Publisher

logger = logging.getLogger(__file__)


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
            '--test-xslt', action='store_true', dest='test_xslt', default=False,
            help='Test the XSLT transformation of articles')

        parser.add_argument(
            '--pid', action='store', dest='journal_pid', help='Journal PID to manually import.')

        parser.add_argument(
            '--mdate', action='store', dest='mdate',
            help='Modification date to use to retrieve journals to import (iso format).')

    def handle(self, *args, **options):
        self.full_import = options.get('full', False)
        self.test_xslt = options.get('test_xslt', False)
        self.journal_pid = options.get('journal_pid', None)
        self.modification_date = options.get('mdate', None)

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
            return

        # Imports each collection
        journal_count, journal_errored_count, issue_count, article_count = 0, 0, 0, 0
        for collection_code in erudit_settings.FEDORA_COLLECTIONS:
            try:
                collection = Collection.objects.get(code=collection_code)
            except Collection.DoesNotExist:
                msg = 'The "{0}" collection is not available.'.format(collection_code)
                logger.error(msg, exc_info=True)
                self.stdout.write(self.style.ERROR(msg))
            else:
                _jc, _jec, _ic, _ac = self.import_collection(collection)
                journal_count += _jc
                journal_errored_count += _jec
                issue_count += _ic
                article_count += _ac

        self.stdout.write(self.style.MIGRATE_HEADING(
            '\nJournals imported: {journal_count} / Journals errored: {journal_errored_count} / '
            'issues imported: {issue_count} / articles imported: {article_count}'.format(
                journal_count=journal_count, journal_errored_count=journal_errored_count,
                issue_count=issue_count, article_count=article_count,
            )))

    def import_collection(self, collection):
        """ Imports all the journals of a specific collection. """
        self.stdout.write(self.style.MIGRATE_HEADING(
            'Start importing "{}" collection'.format(collection.code)))

        latest_update_date = self.modification_date
        if not self.full_import and latest_update_date is None:
            # Tries to fetch the date of the Journal instance with the more recent update date.
            latest_journal_update = Journal.objects.order_by('-fedora_updated').first()
            latest_update_date = latest_journal_update.fedora_updated.date() \
                if latest_journal_update else None

        # STEP 1: fetches the PIDs of the journals that will be imported
        # --

        base_fedora_query = "pid~erudit:{collectionid}.* label='Series Erudit'".format(
            collectionid=collection.localidentifier)
        if self.full_import or latest_update_date is None:
            if not self.full_import:
                self.stdout.write(self.style.WARNING(
                    '  No journals found... proceed to full import!'.format(collection.code)))
            journal_pids = self._get_journal_pids_to_import(base_fedora_query)
        else:
            self.stdout.write(
                '  Importing objects modified since {}.'.format(latest_update_date.isoformat()))
            # Fetches the PIDs of all the journals that have been update since the latest
            # modification date.
            journal_pids = self._get_journal_pids_to_import(
                base_fedora_query + ' mdate>{}'.format(latest_update_date.isoformat()))

        # STEP 2: import each journal using its PID
        # --

        journal_count, journal_errored_count, issue_count, article_count = 0, 0, 0, 0
        for jpid in journal_pids:
            try:
                _ic, _ac = self.import_journal(jpid, collection)
            except Exception as e:
                journal_errored_count += 1
                self.stdout.write(self.style.ERROR(
                    '    Unable to import the journal with PID "{0}": {1}'.format(jpid, e)))
            else:
                journal_count += 1
                issue_count += _ic
                article_count += _ac

        return journal_count, journal_errored_count, issue_count, article_count

    @transaction.atomic
    def import_journal(self, journal_pid, collection):
        """ Imports a journal using its PID. """
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

        # Fetches the Journal instance... or creates a new one
        journal_localidentifier = journal_pid.split('.')[-1]
        try:
            journal = Journal.objects.get(localidentifier=journal_localidentifier)
        except Journal.DoesNotExist:
            journal = Journal()
            journal.localidentifier = journal_localidentifier
            journal.collection = collection
            journal.fedora_created = fedora_journal.created

        oaiset_info_tree = remove_xml_namespaces(
            et.fromstring(fedora_journal.oaiset_info.content.serialize()))
        publications_tree = remove_xml_namespaces(
            et.fromstring(fedora_journal.publications.content.serialize()))

        # Set the proper values on the Journal instance
        xml_name = oaiset_info_tree.find('.//title')
        xml_issue = publications_tree.xpath(
            './/numero[starts-with(@pid, "{0}")]'.format(journal_pid))
        journal.name = xml_name.text if xml_name is not None else None
        journal.code = xml_issue[0].get('revAbr') if xml_issue is not None else None

        journal_created = journal.id is None

        journal.fedora_updated = fedora_journal.modified
        journal.save()

        # Associates the publisher to the Journal instance
        xml_publisher = oaiset_info_tree.find('.//publisher')
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

        issue_count, article_count = 0, 0

        xml_issue_nodes = publications_tree.findall('.//numero')
        for issue_node in xml_issue_nodes:
            ipid = issue_node.get('pid')
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
        issue.volume = issue.erudit_object.volume
        issue.number = issue.erudit_object.number
        issue.title = issue.erudit_object.theme
        issue.date_published = issue.erudit_object.publication_date
        issue.date_produced = issue.erudit_object.production_date \
            or issue.erudit_object.publication_date

        issue.fedora_updated = fedora_issue.modified
        issue.save()

        # STEP 3: patches the journal associated with the issue
        # --

        # Journal name
        self._patch_generic_journal_title(journal, 'name', issue.erudit_object.journal_titles or {})
        self._patch_generic_journal_title(
            journal, 'subtitle', issue.erudit_object.journal_subtitles or {})
        journal.save()

        # STEP 4: imports all the articles associated with the issue
        # --

        article_count = 0

        xml_article_nodes = summary_tree.findall('.//article')
        for article_node in xml_article_nodes:
            try:
                apid = issue_pid + '.{0}'.format(article_node.get('idproprio'))
                self._import_article(apid, issue)
            except Exception as e:
                self.stdout.write(self.style.ERROR('  [FAIL]'))
                logger.error(
                    'The issue\'s article with PID "{0}" cannot be imported: {1}'.format(apid, e),
                    exc_info=True)
                raise
            else:
                article_count += 1

        self.stdout.write(self.style.MIGRATE_SUCCESS('  [OK]'))

        return article_count

    def _import_article(self, article_pid, issue):
        """ Imports an article using its PID. """

        # STEP 1: fetches the full Article fedora object
        # --

        try:
            fedora_article = ArticleDigitalObject(api, article_pid)
            assert fedora_article.exists
        except AssertionError:
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

        # Set the proper values on the Article instance
        processing = article.erudit_object.processing
        processing_mapping = {'minimal': 'M', 'complet': 'C', '': 'M', }
        try:
            article.processing = processing_mapping[processing]
        except KeyError:
            raise ValueError(
                'Unable to determine the processing type of the article '
                'with PID {0}'.format(article_pid))
        article.title = article.erudit_object.title
        article.surtitle = article.erudit_object.section_title

        article.fedora_updated = fedora_article.modified
        article.save()

        # STEP 3: creates or updates the authors of the article
        # --

        for author_xml in article.erudit_object.findall('liminaire//grauteur//auteur'):
            firstname_xml = author_xml.find('.//nompers/prenom')
            firstname = firstname_xml.text if firstname_xml is not None else ''
            lastname_xml = author_xml.find('.//nompers/nomfamille')
            lastname = lastname_xml.text if lastname_xml is not None else ''
            suffix_xml = author_xml.find('.//nompers/suffixe')
            suffix = suffix_xml.text if suffix_xml is not None else None

            author, dummy = Author.objects.get_or_create(
                firstname=firstname, lastname=lastname)
            author.suffix = suffix
            author.save()

            article.authors.add(author)

        # STEP 4: eventually test the XSLT transformation of the article
        # --

        if self.test_xslt:
            try:
                render_article({}, article)
            except Exception as e:
                msg = 'The article with PID "{}" cannot be rendered using XSLT: e'.format(
                    article_pid, e)
                self.stdout.write(self.style.ERROR('      ' + msg))
                logger.error(msg, exc_info=True)

    def _get_journal_pids_to_import(self, query):
        """ Returns the PIDS corresponding to a given Fedora query. """
        self.stdout.write('  Determining journal PIDs to import...', ending='')

        ns_type = {'type': 'http://www.fedora.info/definitions/1/0/types/'}
        journal_pids = []
        session_token = None
        remaining_pids = True

        while remaining_pids:
            # The session token is used by the Fedora Commons repository to paginate a list of
            # results. We have to use it in order to construct the list of PIDs to import!
            session_token = session_token.text if session_token is not None else None
            try:
                response = rest_api.findObjects(query, chunksize=1000, session_token=session_token)
                # Tries to fetch the PIDs of the journals by parsing the response
                tree = et.fromstring(response.content)
                pid_nodes = tree.findall('.//type:pid', ns_type)
                session_token = tree.find('./type:listSession//type:token', ns_type)
                _journal_pids = [n.text for n in pid_nodes]
            except RequestFailed as e:
                self.stdout.write(self.style.ERROR('  [FAIL]'))
                logger.error('Unable to fetches the journal PIDs: {0}'.format(e), exc_info=True)
                return
            else:
                journal_pids.extend(_journal_pids)

            remaining_pids = len(_journal_pids) and session_token is not None

        self.stdout.write(self.style.MIGRATE_SUCCESS('  [OK]'))
        if not len(journal_pids):
            self.stdout.write(self.style.WARNING('  No journal PIDs found'))
        else:
            self.stdout.write('  {0} PIDs found!'.format(len(journal_pids)))

        return journal_pids

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
