# -*- coding: utf-8 -*-

import os.path as op
import csv

from django.conf import settings
from django.core.management.base import BaseCommand

from ...models import Journal

FIXTURE_ROOT = getattr(settings, "JOURNAL_FIXTURES", op.join(op.dirname(__file__), "fixtures"))

SUPPORTED_LANGUAGES = [lang[0] for lang in settings.LANGUAGES]


class Command(BaseCommand):
    help = """Import disciplines from XML files"""

    def handle(self, *args, **options):

        with open(FIXTURE_ROOT + "/erudit_libre_acces.csv", "r") as fp:
            reader = csv.reader(fp, delimiter=",", quotechar='"')
            header = next(reader, None)  # noqa
            for row in reader:
                journal_id = row[11]
                open_access_status = row[16].lower()
                try:
                    journal = Journal.legacy_objects.get_by_id(journal_id)
                    if open_access_status == "libre accès":
                        journal.open_access = True
                    elif open_access_status == "accès restreint":
                        pass
                    elif open_access_status == "archives":
                        pass
                    else:
                        raise ValueError(open_access_status)
                    journal.save()
                except Journal.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR("{} does not exist in the database".format(journal_id))
                    )
        with open(FIXTURE_ROOT + "/persee_libre_acces.csv", "r") as fp:
            reader = csv.reader(fp, delimiter=",", quotechar='"')
            header = next(reader, None)  # noqa
            for row in reader:
                journal_name = row[0]
                open_access_status = row[16].lower()
                try:
                    journal = Journal.objects.get(name=journal_name)
                    if open_access_status == "libre accès":
                        journal.open_access = True
                    elif open_access_status == "accès restreint":
                        pass
                    elif open_access_status == "archives":
                        pass
                    else:
                        raise ValueError(open_access_status)
                    journal.save()
                except Journal.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR("{} does not exist in the database".format(journal_name))
                    )
