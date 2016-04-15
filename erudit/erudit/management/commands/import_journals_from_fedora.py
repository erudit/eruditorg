# -*- coding: utf-8 -*-

import logging
import re

from django.core.management.base import BaseCommand
from django.db import transaction
from eruditarticle.utils import remove_xml_namespaces
from eulfedora.util import RequestFailed
import lxml.etree as et

from ...conf import settings as erudit_settings
from ...fedora.objects import ArticleDigitalObject
from ...fedora.objects import JournalDigitalObject
from ...fedora.objects import PublicationDigitalObject
from ...fedora.repository import api
from ...models import Article
from ...models import Author
from ...models import Collection
from ...models import Issue
from ...models import Journal
from ...models import Publisher

logger = logging.getLogger(__file__)


class Command(BaseCommand):
    help = 'Import journals from Fedora'

    def add_arguments(self, parser):
        parser.add_argument(
            '--full', action='store_true', dest='full', default=False,
            help='Perform a full import.')

        parser.add_argument(
            '--pid', action='store', dest='journal_pid', help='Journal PID to manually import.')

    def handle(self, *args, **options):
        self.full_import = options.get('full', False)
        self.journal_pid = options.get('journal_pid', None)

        # Import a journal PID manually
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
        for collection_code in erudit_settings.FEDORA_COLLECTIONS:
            try:
                collection = Collection.objects.get(code=collection_code)
            except Collection.DoesNotExist:
                msg = 'The "{0}" collection is not available.'.format(collection_code)
                logger.error(msg, exc_info=True)
                self.stdout.write(self.style.ERROR(msg))
            else:
                self.import_collection(collection)

    def import_collection(self, collection):
        """ Imports all the journals of a specific collection. """
        self.stdout.write(self.style.MIGRATE_HEADING(
            'Start importing "{}" collection'.format(collection.code)))

        latest_update_date = None
        if not self.full_import:
            # Tries to fetch the date of the Journal instance with the more recent update date.
            latest_journal_update = Journal.objects.order_by('-fedora_updated').first()
            latest_update_date = latest_journal_update.fedora_updated if latest_journal_update \
                else None

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
            # Fetches the PIDs of all the journals that have been update since the latest
            # modification date.
            journal_pids = self._get_journal_pids_to_import(
                base_fedora_query + ' mdate>{}'.format(latest_update_date.date().isoformat()))

        # STEP 2: import each journal using its PID
        # --

        for jpid in journal_pids:
            try:
                self.import_journal(jpid, collection)
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    '    Unable to import the journal with PID "{0}": {1}'.format(jpid, e)))

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
        xml_issue = publications_tree.find('.//numero')
        journal.name = xml_name.text if xml_name is not None else None
        journal.code = xml_issue.get('revAbr') if xml_issue is not None else None

        journal_created = journal.id is None

        journal.fedora_updated = fedora_journal.modified
        journal.save()

        # Associates the publisher to the Journal instance
        xml_publisher = oaiset_info_tree.find('.//publisher')
        publisher_name = xml_publisher.text if xml_publisher is not None else None
        publisher, _ = Publisher.objects.get_or_create(name=publisher_name)
        journal.publishers.add(publisher)

        if journal_created:
            self.stdout.write('      Journal instance created: "{}"'.format(journal.name))
        else:
            self.stdout.write('      Journal instance updated: "{}"'.format(journal.name))

        # STEP 3: imports all the issues associated with the journal
        # --

        xml_issue_nodes = publications_tree.findall('.//numero')
        for issue_node in xml_issue_nodes:
            ipid = issue_node.get('pid')
            self._import_issue(ipid, journal)

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

        # STEP 3: imports all the articles associated with the issue
        # --

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

        self.stdout.write(self.style.MIGRATE_SUCCESS('  [OK]'))

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

    def _get_journal_pids_to_import(self, query):
        """ Returns the PIDS corresponding to a given Fedora query. """
        self.stdout.write('  Determining journal PIDs to import...', ending='')
        try:
            response = api.findObjects(query=query)
            # Tries to fetch the PIDs of the journals by parsing the response
            tree = et.fromstring(response.content)
            pid_nodes = tree.findall(
                './/type:pid', {"type": "http://www.fedora.info/definitions/1/0/types/"})
            journal_pids = [n.text for n in pid_nodes]
        except RequestFailed as e:
            self.stdout.write(self.style.ERROR('  [FAIL]'))
            logger.error('Unable to fetches the journal PIDs: {0}'.format(e), exc_info=True)
            return
        else:
            self.stdout.write(self.style.MIGRATE_SUCCESS('  [OK]'))

        if not len(journal_pids):
            self.stdout.write(self.style.WARNING('  No journal PIDs found'))
        else:
            self.stdout.write('  {0} PIDs found!'.format(len(journal_pids)))

        return journal_pids
