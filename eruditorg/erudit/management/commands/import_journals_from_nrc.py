# -*- coding: utf-8 -*-

import os.path as op

from django.core.management.base import BaseCommand
from django.conf import settings
import lxml.etree as et

from ...models import Collection
from ...models import Journal


FIXTURE_ROOT = getattr(
    settings,
    "JOURNAL_FIXTURES",
    op.join(op.dirname(__file__), "fixtures"),
)


class Command(BaseCommand):
    help = "Import NRC journals from XML files"

    def handle(self, *args, **options):
        # STEP 1: creates the NRC collection
        collection, _ = Collection.objects.get_or_create(code="nrc", name="NRC Research Press")

        # STEP 2: imports the NRC journals
        journals_xml = None
        with open(FIXTURE_ROOT + "/revues.xml", "rb") as fp:
            journals_xml = fp.read()

        if journals_xml:
            dom = et.fromstring(journals_xml)
            for journal_xml in dom.findall('.//revue[@fond="2"]'):
                self.import_journal(collection, journal_xml)
        else:
            self.stdout.write(self.style.ERROR("Unable to import journals"))

    def import_journal(self, collection, journal_xml):
        """ Imports a specific journal using its XML content. """
        self.stdout.write(
            self.style.MIGRATE_LABEL(
                "    Start importing the journal with code: {0}".format(journal_xml.get("code"))
            ),
            ending="",
        )

        # Creates or updates the journal object
        # --

        journal_code = journal_xml.get("code")
        try:
            journal = Journal.objects.get(code=journal_code)
        except Journal.DoesNotExist:
            journal = Journal()
            journal.code = journal_code
            journal.collection = collection

        journal.name = journal_xml.find(".//titreTexte").text
        journal.url = journal_xml.find(".//siteWeb").text

        journal.save()

        self.stdout.write(self.style.SUCCESS("  [OK]"))
