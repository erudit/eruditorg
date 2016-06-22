# -*- coding: utf-8 -*-

import datetime as dt

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.core.validators import URLValidator
from sickle import Sickle

from ...conf import settings as erudit_settings
from ...models import Author
from ...models import Collection
from ...models import Thesis


class Command(BaseCommand):
    """ Imports thesis objects from OAI-PMH providers. """

    help = 'Import thesus from OAI-PMH providers'

    def handle(self, *args, **options):
        # Imports the OAI-based collections
        thesis_count, thesis_errored_count = 0, 0
        for collection_config in erudit_settings.THESIS_PROVIDERS.get('oai'):
            code = collection_config['collection_code']
            name = collection_config['collection_title']
            endpoint = collection_config['endpoint']
            setspecs = collection_config.get('sets', [None, ])
            try:
                collection = Collection.objects.get(code=code)
            except Collection.DoesNotExist:
                collection = Collection.objects.create(code=code, name=name)
            for setspec in setspecs:
                _jc, _jec = self.import_collection(collection, endpoint, setspec)
                thesis_count += _jc
                thesis_errored_count += _jec

        self.stdout.write(self.style.MIGRATE_HEADING(
            '\nTheses imported: {thesis_count} /'
            ' Theses errored: {thesis_errored_count}'.format(
                thesis_count=thesis_count, thesis_errored_count=thesis_errored_count,
            )))

    def import_collection(self, collection, endpoint, setspec):
        """ Imports all the theses of a specific collection. """
        self.stdout.write(self.style.MIGRATE_HEADING(
            'Start importing "{}" collection'.format(collection.code)))

        sickle = Sickle(endpoint)

        # STEP 1: initializes an iterator of records using the "GetRecords" method
        # --

        records = sickle.ListRecords(metadataPrefix='oai_dc', set=setspec)

        # STEP 2: imports each thesis
        # --

        thesis_count, thesis_errored_count = 0, 0
        for record in records:
            try:
                assert not record.deleted
                self.import_thesis(record, collection)
            except AssertionError:
                pass
            except Exception as e:
                thesis_errored_count += 1
                self.stdout.write(self.style.ERROR(
                    '    Unable to import the thesis with identifier "{0}": {1}'.format(
                        record.header.identifier, e)))
            else:
                thesis_count += 1

        return thesis_count, thesis_errored_count

    def import_thesis(self, record, collection):
        """ Imports a specific thesus using its recored returned by an OAI-PMH provider. """
        self.stdout.write(self.style.MIGRATE_LABEL(
            '    Start importing the thesis with identifier: {0}'.format(record.header.identifier)),
            ending='')

        oai_ns = {
            'dc': 'http://purl.org/dc/elements/1.1/',
            'oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
        }

        # Checks the data embedded into the record
        title = record.xml.find('.//dc:title', oai_ns).text
        author_name = record.xml.find('.//dc:creator', oai_ns).text
        dates = record.metadata.get('date', None)
        if title is None or author_name is None or dates is None:
            self.stdout.write(self.style.WARNING('  Unable to import due to missing data'))
            return

        # Creates or updates the thesis object
        # --

        localidentifier = record.header.identifier
        try:
            thesis = Thesis.objects.get(collection=collection, localidentifier=localidentifier)
        except Thesis.DoesNotExist:
            thesis = Thesis()
            thesis.localidentifier = localidentifier
            thesis.collection = collection

        thesis.title = title

        author = thesis.author if thesis.author_id else Author()
        author_name_split = author_name.split(',')
        author.lastname = author_name_split[0].strip()
        author.firstname = author_name_split[1].strip() if len(author_name_split) > 1 else None
        author.save()
        thesis.author = author

        # Determines the URL of the thesis
        for id_node in record.xml.findall('.//dc:identifier', oai_ns):
            try:
                URLValidator()(id_node.text)
            except ValidationError:
                pass
            else:
                thesis.url = id_node.text
                break

        # Determines the publication year of the thesis
        date_formats = ['%Y-%m-%d', '%Y-%m', '%B %Y', '%Y.', '%Y', ]
        for sdate in record.metadata['date']:
            sdate = sdate.strip()
            for dformat in date_formats:
                try:
                    pdate = dt.datetime.strptime(sdate, dformat).date()
                    thesis.publication_year = pdate.year
                    break
                except ValueError:
                    pdate = None

            if pdate:
                break

        thesis_description = record.metadata.get('description', None)
        thesis.description = thesis_description[0] if thesis_description else None

        thesis.save()

        self.stdout.write(self.style.MIGRATE_SUCCESS('  [OK]'))
