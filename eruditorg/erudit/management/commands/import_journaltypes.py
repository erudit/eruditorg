# -*- coding: utf-8 -*-

import os.path as op

from django.conf import settings
from django.core.management.base import BaseCommand
import lxml.etree as et

from ...models import Journal, JournalType

FIXTURE_ROOT = getattr(settings, "JOURNAL_FIXTURES", op.join(op.dirname(__file__), "fixtures"))

SUPPORTED_LANGUAGES = [lang[0] for lang in settings.LANGUAGES]


class Command(BaseCommand):
    help = """Import disciplines from XML files"""

    def get_journal_query(self, code, type_code):
        """Return a dict containing params of the ORM query"""
        if type_code == "C":
            return {"localidentifier": code}
        else:
            return {"code": code}

    def assign_type_to_journal(self, filename, type_code):
        """Assign the JournalType identified by type_code
        to the journals in the file `filename`
        """
        with open(FIXTURE_ROOT + filename, "rb") as fp:
            xml = fp.read()
            dom = et.fromstring(xml)

            try:
                journal_type = JournalType.objects.get(code=type_code)
            except JournalType.DoesNotExist:
                print("Unable to find the JournalType with code: {}".format("s"))
                raise

            for journal_xml in dom.findall(".//revue"):
                try:
                    journal = Journal.objects.get(
                        **self.get_journal_query(journal_xml.get("code"), type_code)
                    )
                    journal.type = journal_type
                    journal.save()
                except Journal.DoesNotExist:
                    print(
                        "Unable to find the following Journal instance: {}".format(
                            journal_xml.get("code")
                        )
                    )
                    continue

    def handle(self, *args, **options):
        self.assign_type_to_journal("/revues.xml", "S")
        self.assign_type_to_journal("/revues_culturelle.xml", "C")
