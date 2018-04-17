import structlog
import csv

from datetime import datetime

from django.core.management.base import BaseCommand

from erudit.models import Journal

from core.subscription.models import JournalManagementSubscription


logger = structlog.get_logger(__name__)

import_date = datetime.now()
end_date = datetime(month=12, day=31, year=2017)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--filename', action="store", dest="filename"
        )

        parser.add_argument(
            '--shortname', action='store', dest='shortname', help='Journal shortname.'
        )

    def handle(self, *args, **options):
        """
        Command dispatcher
        """

        journal_shortname = options.get('shortname')
        filename = options.get('filename')

        journal = None
        plan = None

        try:
            journal = Journal.objects.get(code=journal_shortname)
            plan = JournalManagementSubscription.objects.get(journal=journal)
        except Journal.DoesNotExist:
            self.stdout.write("Journal {} does not exist".format(journal_shortname))
            raise
        except JournalManagementSubscription.DoesNotExist:
            self.stdout.write("Journal {} has no plan.".format(journal_shortname))
            raise

        with open(filename, 'r', encoding="utf-8") as csv_file:
            csvreader = csv.reader(csv_file)
            self.subscriptions = [tuple(row) for row in csvreader]

        for email, firstname, lastname in self.subscriptions:
            plan.subscribe_email(email, firstname=firstname, lastname=lastname)
