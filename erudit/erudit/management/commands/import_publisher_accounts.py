import logging

from erudit.models.core import Publisher, Journal

from erudit.utils.edinum import (
    fetch_publishers_from_edinum,
    fetch_publisher_journals_from_edinum,
    create_or_update_publisher,
    create_or_update_journal
)

from django.core.management.base import BaseCommand

log = logging.getLogger(__name__)


class Command(BaseCommand):

    help = """Import publisher accounts from edinum"""

    def handle(self, *args, **options):
        self.created_or_updated_publishers = []
        self.created_or_updated_journals = []

        for publisher_row in fetch_publishers_from_edinum():
            (person_id, publisher_name, series_id, journal_id,
             journal_name, journal_shortname, journal_localidentifier,
             journal_subtitle) = publisher_row

            if person_id not in self.created_or_updated_publishers:
                publisher = create_or_update_publisher(
                    person_id,
                    publisher_name
                )

                self.created_or_updated_publishers.append(person_id)

            create_or_update_journal(
                publisher,
                journal_id,
                journal_name,
                journal_shortname,
                journal_localidentifier,
                journal_subtitle
            )

            self.created_or_updated_journals.append(journal_shortname)

        publisher_journals = fetch_publisher_journals_from_edinum()

        for journal_sn in self.created_or_updated_journals:
            journal = Journal.objects.get(code=journal_sn)
            # journal.publishers.all().delete()
            for publisher_id, journal_id in publisher_journals:
                if journal_id == journal.edinum_id:
                    publisher = Publisher.objects.get(edinum_id=publisher_id)
                    journal.publishers.add(publisher)
