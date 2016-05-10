# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.core.validators import URLValidator
from sickle import Sickle

from ...conf import settings as erudit_settings
from ...models import Collection
from ...models import Journal


class Command(BaseCommand):
    """ Imports journal objects from the OAI-PMH providers. """

    help = 'Import journals from OAI-PMH providers'

    def handle(self, *args, **options):
        # Imports the OAI-based collections
        journal_count, journal_errored_count = 0, 0
        for code, collection_config in erudit_settings.OAI_PROVIDERS.items():
            name = collection_config['name']
            endpoint = collection_config['endpoint']
            try:
                collection = Collection.objects.get(code=code)
            except Collection.DoesNotExist:
                collection = Collection.objects.create(code=code, name=name)
            _jc, _jec = self.import_collection(collection, endpoint)
            journal_count += _jc
            journal_errored_count += _jec

        self.stdout.write(self.style.MIGRATE_HEADING(
            '\nJournals imported: {journal_count} /'
            ' Journals errored: {journal_errored_count}'.format(
                journal_count=journal_count, journal_errored_count=journal_errored_count,
            )))

    def import_collection(self, collection, endpoint):
        """ Imports all the journals of a specific collection. """
        self.stdout.write(self.style.MIGRATE_HEADING(
            'Start importing "{}" collection'.format(collection.code)))

        sickle = Sickle(endpoint)

        # STEP 1: initializes an iterator of "sets" using the "ListSets" method
        # --

        journal_sets = sickle.ListSets()

        # STEP 2: imports each journal
        # --

        journal_count, journal_errored_count = 0, 0
        for journal_set in journal_sets:
            try:
                assert journal_set.setSpec.startswith('serie')
                self.import_journal(journal_set, collection)
            except AssertionError:
                pass
            except Exception as e:
                journal_errored_count += 1
                self.stdout.write(self.style.ERROR(
                    '    Unable to import the journal with spec "{0}": {1}'.format(
                        journal_set.setSpec, e)))
            else:
                journal_count += 1

        return journal_count, journal_errored_count

    def import_journal(self, journal_set, collection):
        """ Imports a specific journal using its journal set return by an OAI-PMH provider. """
        self.stdout.write(self.style.MIGRATE_LABEL(
            '    Start importing the journal with spec: {0}'.format(journal_set.setSpec)),
            ending='')

        oai_ns = {
            'dc': 'http://purl.org/dc/elements/1.1/',
            'oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
        }

        # Creates or updates the journal object
        # --

        journal_code = '{collection_code}{spec}'.format(
            collection_code=collection.code, spec=journal_set.setSpec.split(':')[-1])
        try:
            journal = Journal.objects.get(code=journal_code)
        except Journal.DoesNotExist:
            journal = Journal()
            journal.code = journal_code
            journal.collection = collection

        journal.name = journal_set.title if hasattr(journal_set, 'title') else journal_set.setName

        # Determines the URL of the journal
        for id_node in journal_set.xml.findall('.//dc:identifier', oai_ns):
            try:
                URLValidator()(id_node.text)
            except ValidationError:
                pass
            else:
                journal.url = id_node.text
                break

        journal.save()

        self.stdout.write(self.style.MIGRATE_SUCCESS('  [OK]'))
