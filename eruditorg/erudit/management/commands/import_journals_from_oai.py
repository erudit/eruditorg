# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from sickle import Sickle

from ...conf import settings as erudit_settings
from ...models import Collection


class Command(BaseCommand):
    """ Imports journal objects from the OAI-PMH providers. """

    help = 'Import journals from OAI-PMH providers'

    def handle(self, *args, **options):
        # Imports the OAI-based collections
        for code, collection_config in erudit_settings.OAI_PROVIDERS.items():
            name = collection_config['name']
            endpoint = collection_config['endpoint']
            try:
                collection = Collection.objects.get(code=code)
            except Collection.DoesNotExist:
                collection = Collection.objects.create(code=code, name=name)
            self.import_collection(collection, endpoint)

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

        for journal_set in journal_sets:
            self.import_journal(journal_set, collection)

    def import_journal(self, journal_set, collection):
        """ Imports a specific journal using its journal set return by an OAI-PMH provider. """
        pass
