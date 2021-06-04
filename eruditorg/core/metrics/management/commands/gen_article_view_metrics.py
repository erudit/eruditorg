import datetime as dt
import random

from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand
from django.db.models import Q

from core.subscription.models import JournalAccessSubscription
from erudit.solr.models import get_all_articles

from ...metric import metric


class Command(BaseCommand):
    help = "Generates article views metrics for a given period of time"

    def add_arguments(self, parser):
        parser.add_argument(
            "--number",
            action="store",
            dest="number",
            type=int,
            default=1000,
            help="Number of metric points to generate",
        )
        parser.add_argument(
            "--start",
            action="store",
            dest="sdate",
            help="Start date from which the points will be generated (ISO format) "
            "- defaults to the current date minus 4 years",
        )

    def handle(self, *args, **options):
        number = options.get("number")
        start_date = options.get("sdate", None)

        # Determines the start datetime to use
        try:
            assert start_date is not None
            start_date = dt.datetime.strptime(start_date, "%Y-%m-%d").date()
            start = dt.datetime.combine(start_date, dt.datetime.min.time())
        except ValueError:
            self.stdout.write(
                self.style.ERROR('"{0}" is not a valid modification date!'.format(start_date))
            )
            return
        except AssertionError:
            start = dt.datetime.now() - relativedelta(years=4)

        end = dt.datetime.now()

        if start > end:
            self.stdout.write(self.style.ERROR("You cannot use a date that is in the future!"))
            return

        total_seconds = int((end - start).total_seconds())
        articles = get_all_articles(rows=10 ** 6, page=1)["items"]

        # Generates metrics
        for i in range(number):
            article = random.choice(articles)
            subscription = (
                JournalAccessSubscription.objects.filter(
                    Q(journals__id=article.issue.journal_id), organisation__isnull=False
                )
                .order_by("?")
                .first()
            )
            subscription_id = subscription.id if subscription is not None else None
            dtime = start + dt.timedelta(seconds=random.randint(0, total_seconds))
            metric(
                "erudit__journal__article_view",
                time=dtime,
                tags={
                    "journal_localidentifier": article.issue.journal.localidentifier,
                    "open_access": article.open_access or not article.embargoed,
                    "view_type": random.choice(
                        [
                            "html",
                            "pdf",
                        ]
                    ),
                },
                **{
                    "issue_localidentifier": article.issue.localidentifier,
                    "localidentifier": article.localidentifier,
                    "subscription_id": subscription_id,
                }
            )
            self.stdout.write(
                self.style.MIGRATE_LABEL("Generated point {i}/{number}".format(i=i, number=number))
            )
