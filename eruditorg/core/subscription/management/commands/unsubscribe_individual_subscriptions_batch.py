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

        for email, in self.subscriptions:
            try:
                user = User.objects.get(email=email)
                subscription = JournalAccessSubscription.objects.get(
                    journal_management_subscription=plan, user=user
                )
                subscription.delete()
                logger.info(
                    "subscription.deleted",
                    user=user.username,
                    journal=journal_shortname,
                    plan=plan.pk
                )
            except User.DoesNotExist:
                logger.error("user.doesnotexist", email=email)
            except User.MultipleObjectsReturned:
                logger.error("user.multipleobjectsreturned", email=email)
                raise
            except JournalAccessSubscription.MultipleObjectsReturned:
                deleted = JournalAccessSubscription.objects.filter(
                    journal_management_subscription=plan, user=user
                ).delete()
                logger.warn(
                    "subscription.MultipleObjectsReturned",
                    user=user,
                    journal_management_subscription=plan.pk,
                    deleted=deleted
                )

            except JournalAccessSubscription.DoesNotExist:
                logger.error(
                    "subscription.doesnotexist",
                    user=user,
                    journal=journal_shortname,
                    plan=plan.pk
                )
