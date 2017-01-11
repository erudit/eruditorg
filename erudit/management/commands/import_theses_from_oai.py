# -*- coding: utf-8 -*-

import datetime as dt

from dateutil.parser import parse as dt_parse
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.core.validators import URLValidator
from django.db.models import Q
from django.template.defaultfilters import slugify
from sickle import Sickle

from ...conf import settings as erudit_settings
from ...models import Author
from ...models import Collection
from ...models import KeywordTag
from ...models import Thesis


class Command(BaseCommand):
    """ Imports thesis objects from OAI-PMH providers. """

    help = 'Import theses from OAI-PMH providers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--full', action='store_true', dest='full', default=False,
            help='Perform a full import.')

        parser.add_argument(
            '--mdate', action='store', dest='mdate',
            help='Modification date to use to retrieve theses to import (iso format).')

        parser.add_argument(
            '--collection', action='store', dest='collection',
            help='Collection to import'
        )

    def handle(self, *args, **options):
        self.full_import = options.get('full', False)
        self.modification_date = options.get('mdate', None)
        self.collection = options.get('collection', None)

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
        thesis_count, thesis_errored_count = 0, 0
        for collection_config in erudit_settings.THESIS_PROVIDERS.get('oai'):
            if self.collection and collection_config['collection_code'] != self.collection:
                continue
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

        latest_update_date = self.modification_date
        if not self.full_import and latest_update_date is None:
            # Tries to fetch the date of the Thesis instance with the more recent update date.
            latest_thesis_updated = Thesis.objects \
                .filter(collection=collection, oai_datestamp__isnull=False) \
                .order_by('-oai_datestamp').first()
            latest_update_date = latest_thesis_updated.oai_datestamp.date() \
                if latest_thesis_updated else None

        sickle = Sickle(endpoint)

        # STEP 1: initializes an iterator of records using the "GetRecords" method
        # --

        oai_request_params = {'metadataPrefix': 'oai_dc', 'set': setspec}
        if self.full_import or latest_update_date is None:
            if not self.full_import:
                self.stdout.write(self.style.WARNING(
                    '  No theses found... proceed to full import!'))
        else:
            self.stdout.write(
                '  Importing theses modified since {}.'.format(latest_update_date.isoformat()))
            oai_request_params.update({'from': latest_update_date.isoformat()})

        records = sickle.ListRecords(**oai_request_params)

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
        thesis.oai_datestamp = dt_parse(record.header.datestamp)

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

        # Associates the keywords with the Thesis instance
        keywords = list(set(record.metadata.get('subject', [])))
        for kword in keywords:
            if not kword:
                continue

            try:
                tag = KeywordTag.objects.filter(
                    Q(slug=slugify(kword)[:100]) | Q(name=kword[:100])).first()
                assert tag is not None
            except AssertionError:
                tag = kword
            thesis.keywords.add(tag)

        self.stdout.write(self.style.SUCCESS('  [OK]'))
