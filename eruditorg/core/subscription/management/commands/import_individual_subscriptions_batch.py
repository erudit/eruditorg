import structlog
import csv

from datetime import datetime

from django.core.management.base import BaseCommand

from erudit.models import Journal

from core.subscription.models import (
    JournalManagementSubscription, JournalAccessSubscription, Organisation, AccessBasket
)
from django.contrib.auth import get_user_model

logger = structlog.get_logger(__name__)

import_date = datetime.now()
end_date = datetime(month=12, day=31, year=2017)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--filename', action="store", dest="filename"
        )

        parser.add_argument(
            '--use-journal-plan', action='store_true', dest='use_journal_plan',
            help="Use the journal's plan."
        )

        parser.add_argument(
            '--shortname', action='store', dest='shortname', help='Journal shortname.'
        )

        parser.add_argument(
            '--plan-id', action='store', dest='plan_id', help='Plan id.'
        )

        parser.add_argument(
            '--sponsor-id', action='store', dest='sponsor_id', help='Sponsor id.'
        )

        parser.add_argument(
            '--basket-id', action='store', dest='basket_id', help='Basket id.'
        )

    def handle(self, *args, **options):
        """
        Command dispatcher
        """
        journal_shortname = options.get('shortname')
        use_journal_plan = options.get('use_journal_plan')
        sponsor_id = options.get("sponsor_id")
        plan_id = options.get("plan_id")
        filename = options.get("filename")
        basket_id = options.get("basket_id")

        with open(filename, 'r', encoding="utf-8") as csv_file:
            csvreader = csv.reader(csv_file, delimiter=";")
            self.subscriptions = [tuple(row) for row in csvreader]

            for value in self.subscriptions:
                print(value)
                email, first_name, last_name = value
                if use_journal_plan and journal_shortname:
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

                    plan.subscribe_email(email, firstname=first_name, lastname=last_name)
                else:
                    user, _ = get_user_model().objects.get_or_create(
                        email=email,
                        defaults={
                            "username": email,
                            "first_name": first_name,
                            "last_name": last_name
                        }
                    )

                    subscription = JournalAccessSubscription(user=user)
                    if sponsor_id:
                        if sponsor_id:
                            subscription.sponsor = Organisation.objects.get(pk=sponsor_id)
                        if plan_id:
                            subscription.journal_management_subscription = \
                                JournalManagementSubscription.objects.get(
                                    pk=plan_id
                                )
                        if basket_id:
                            subscription.basket = AccessBasket.objects.get(pk=basket_id)
                    subscription.save()
