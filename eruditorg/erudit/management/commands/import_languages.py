# -*- coding: utf-8 -*-

import csv

from django.core.management.base import BaseCommand

from ...models import JournalInformation, Journal
from ...models import Language


class Command(BaseCommand):
    help = """Import disciplines from XML files"""

    def add_arguments(self, parser):
        parser.add_argument(
            'filename', action='store', default=False,
            help='Name of the file containing the Journal -> Language associations.')

    def handle(self, *args, **options):
        with open(options.get('filename'), newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                shortname = row[0]
                languages = row[12].split('/')
                status = row[4]
                if status == "à paraître":
                    continue

                try:
                    journal = Journal.legacy_objects.get_by_id(shortname)
                    info = JournalInformation.objects.get(journal=journal)
                    if len(languages) == 0:
                        raise Exception
                    else:
                        for language in languages:
                            if language == '':
                                language = 'fr'
                            info.languages.add(Language.objects.get(code=language.lower()))
                    info.save()
                except Journal.DoesNotExist:
                    print("Journal.DoesNotExist: {}".format(row))
                except JournalInformation.DoesNotExist:
                    print("JournalInformation.DoesNotExist: {}".format(row))
        print(options.get('filename'))
