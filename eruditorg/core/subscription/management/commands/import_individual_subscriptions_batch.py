import structlog
import csv

from datetime import datetime

from django.core.management.base import BaseCommand

from erudit.models import Journal

from core.subscription.models import (
    JournalAccessSubscription, JournalManagementSubscription
)
from django.contrib.auth.models import User

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
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = User(email=email, username=email, first_name=firstname, last_name=lastname)
                user.save()
                logger.info("user.created", user=user.username)
            finally:
                try:
                    JournalAccessSubscription.objects.get(
                        journal_management_subscription=plan, user=user
                    )
                except JournalAccessSubscription.DoesNotExist:
                    subscription = JournalAccessSubscription(
                        journal_management_subscription=plan, user=user
                    )
                    subscription.save()
                    subscription.journals.add(journal)
                    subscription.save()
                    logger.info(
                        "subscription.created",
                        user=user.username, journal=journal_shortname, plan=plan.pk
                    )
