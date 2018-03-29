import datetime as dt
import logging

from dateutil.parser import parse as dt_parse
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.core.validators import URLValidator
from django.db import transaction
from sickle import Sickle
from sickle.oaiexceptions import BadResumptionToken

from ...conf import settings as erudit_settings
from ...models import Collection
from ...models import Issue
from ...models import Journal
from ...models import JournalType

logger = logging.getLogger(__name__)
scientific_journal_type = JournalType.objects.get(code=JournalType.CODE_SCIENTIFIC)


class Command(BaseCommand):
    """ Imports journal objects from the OAI-PMH providers. """

    help = 'Import journals from OAI-PMH providers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--full', action='store_true', dest='full', default=False,
            help='Perform a full import.')

        parser.add_argument(
            '--mdate', action='store', dest='mdate',
            help='Modification date to use to retrieve journals to import (iso format).')

        parser.add_argument(
            '--collection-code', action='append', dest='collection_code',
            help='')

        parser.add_argument(
            '--journal-code', action='append', dest='journal_code',
            help='')

    def handle(self, *args, **options):
        self.full_import = options.get('full', False)
        self.modification_date = options.get('mdate', None)
        self.collection_codes = options.get('collection_code', None)
        self.journal_codes = options.get('journal_code', None)

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

        # Imports the OAI-based collections
        journal_count, journal_errored_count, issue_count = 0, 0, 0
        for collection_config in erudit_settings.JOURNAL_PROVIDERS.get('oai'):
            code = collection_config['collection_code']
            if self.collection_codes and code not in self.collection_codes:
                self.stdout.write(self.style.MIGRATE_HEADING(
                    'Collection code is specified and {0} is not in the list: skipping'.format(
                        code
                    )
                ))
                continue
            name = collection_config['collection_title']
            endpoint = collection_config['endpoint']

            try:
                collection = Collection.objects.get(code=code)
            except Collection.DoesNotExist:
                collection = Collection.objects.create(code=code, name=name)
            _jc, _jec, _ic = \
                self.import_collection(collection, endpoint, collection_config)
            journal_count += _jc
            journal_errored_count += _jec
            issue_count += _ic

        self.stdout.write(self.style.MIGRATE_HEADING(
            '\nJournals imported: {journal_count} / Journals errored: {journal_errored_count} / '
            'issues imported: {issue_count}'.format(
                journal_count=journal_count, journal_errored_count=journal_errored_count,
                issue_count=issue_count
            )))

    def import_collection(self, collection, endpoint, oai_config):
        """ Imports all the journals of a specific collection. """
        self.stdout.write(self.style.MIGRATE_HEADING(
            'Start importing "{}" collection'.format(collection.code)))

        sickle = Sickle(endpoint, encoding='utf-8')

        # STEP 1: initializes an iterator of "sets" using the "ListSets" method
        # --

        journal_sets = sickle.ListSets()

        # STEP 2: imports each journal
        # --

        journal_count, journal_errored_count, issue_count = 0, 0, 0
        for journal_set in journal_sets:

            try:
                assert journal_set.setSpec.startswith('serie')\
                    and not journal_set.setSpec.startswith('series')
                _, _, journal_code = journal_set.setSpec.split(':')
                if self.journal_codes and journal_code not in self.journal_codes:
                    self.stdout.write(self.style.MIGRATE_HEADING(
                        'Journal code is specified and {0} is not in the list: skipping'.format(
                            journal_code
                        )
                    ))
                    continue
                _ic = self.import_journal(journal_set, collection, oai_config, sickle)
            except AssertionError:
                pass
            except BadResumptionToken as e:
                msg = 'Bad resumption token when importing journal with spec "{0}": {1} ' \
                      'Some issues could have not been imported...'.format(journal_set.setSpec, e)
                logger.warning(msg, exc_info=True)
                self.stdout.write(self.style.WARNING('    ' + msg))
            except Exception as e:
                journal_errored_count += 1
                msg = 'Unable to import the journal with spec "{0}": {1}'.format(
                    journal_set.setSpec, e)
                logger.error(msg, exc_info=True)
                self.stdout.write(self.style.ERROR('    ' + msg))
            else:
                journal_count += 1
                issue_count += _ic

        return journal_count, journal_errored_count, issue_count

    def import_journal(self, journal_set, collection, oai_config, sickle):
        """ Imports a specific journal using its journal set return by an OAI-PMH provider. """
        self.stdout.write(self.style.MIGRATE_LABEL(
            '    Start importing the journal with spec: {0}'.format(journal_set.setSpec)))

        oai_ns = {
            'dc': 'http://purl.org/dc/elements/1.1/',
            'oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
        }

        # STEP 1: Creates or updates the journal object
        # --
        journal_code = '{collection_code}{spec}'.format(
            collection_code=collection.code, spec=journal_set.setSpec.split(':')[-1])
        try:
            journal = Journal.objects.get(code=journal_code)
        except Journal.DoesNotExist:
            journal = Journal()
            journal.code = journal_code
            journal.redirect_to_external_url = True
            journal.type = scientific_journal_type
        journal.collection = collection
        journal.name = journal_set.title if hasattr(journal_set, 'title') else journal_set.setName

        # Determines the URL of the journal
        for id_node in journal_set.xml.findall('.//dc:identifier', oai_ns):
            try:
                URLValidator()(id_node.text)
            except ValidationError:
                pass
            else:
                journal.external_url = id_node.text
                break

        journal.save()

        # STEP 2: imports each issue
        # --

        latest_update_date = self.modification_date
        if not self.full_import and latest_update_date is None:
            # Tries to fetch the date of the Thesis instance with the more recent update date.
            latest_issue_updated = Issue.objects \
                .filter(journal=journal, oai_datestamp__isnull=False) \
                .order_by('-oai_datestamp').first()
            latest_update_date = latest_issue_updated.oai_datestamp.date() \
                if latest_issue_updated else None

        issue_metadataprefix = oai_config.get('issue_metadataprefix')
        oai_request_params = {'metadataPrefix': issue_metadataprefix, 'set': journal_set.setSpec}
        if self.full_import or latest_update_date is None:
            if not self.full_import:
                self.stdout.write(self.style.WARNING(
                    '      No issues found... proceed to full import!'))
        else:
            self.stdout.write(
                '      Importing issues modified since {}.'.format(latest_update_date.isoformat()))
            oai_request_params.update({'from': latest_update_date.isoformat()})

        issue_records = sickle.ListRecords(**oai_request_params)

        issue_count = 0
        for issue_record in issue_records:
            with transaction.atomic():
                try:
                    if issue_metadataprefix == 'persee_mets':
                        self._import_issue_from_persee_mets(
                            issue_record, journal, oai_config, sickle)
                    else:
                        raise NotImplementedError
                except Exception as e:
                    msg = 'Unable to import the issue with identifier "{0}": {1}'.format(
                        issue_record.header.identifier, e)
                    logger.error(msg, exc_info=True)
                    self.stdout.write(self.style.ERROR('    ' + msg))
                else:
                    issue_count += 1

        return issue_count

    def _import_issue_from_persee_mets(self, issue_record, journal, oai_config, sickle):
        self.stdout.write(
            '      Importing issue with identifier "{0}"...'.format(
                issue_record.header.identifier), ending='')

        oai_ns = {
            'dc': 'http://purl.org/dc/elements/1.1/',
            'mets': 'http://www.loc.gov/mets/',
            'oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
            'openurl': 'info:ofi/fmt:xml:xsd:journal',
        }

        # STEP 1: creates or updates the issue object
        # --

        issue_localidentifier = 'num-' + issue_record.header.identifier.split('/')[-1]
        try:
            issue = Issue.objects.get(localidentifier=issue_localidentifier)
        except Issue.DoesNotExist:
            issue = Issue()
            issue.localidentifier = issue_localidentifier
            issue.journal = journal

        # Set the proper values on the Issue instance

        volume_xml = issue_record.xml.find('.//openurl:volume', oai_ns)
        number_xml = issue_record.xml.find('.//openurl:issue', oai_ns)
        year_xml = issue_record.xml.find('.//openurl:date', oai_ns)
        external_url_xml = issue_record.xml.find('.//dc:identifier[@scheme="URL"]', oai_ns)

        issue.volume = volume_xml.text if volume_xml is not None else None
        issue.number = number_xml.text if number_xml is not None else None
        issue.year = year_xml.text if year_xml is not None else None
        issue.date_published = dt.datetime(year=int(issue.year), month=1, day=1)
        issue.external_url = external_url_xml.text if external_url_xml is not None else None
        issue.oai_datestamp = dt_parse(issue_record.header.datestamp)

        issue.save()

        self.stdout.write(self.style.SUCCESS('  [OK]'))
