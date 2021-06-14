import sentry_sdk
import structlog

import datetime as dt
import os.path as op

from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

from erudit.models import Journal
from erudit.models import Organisation

from core.accounts.models import LegacyAccountProfile
from core.accounts.shortcuts import get_or_create_legacy_user
from core.subscription.models import InstitutionIPAddressRange
from core.subscription.models import JournalAccessSubscription
from core.subscription.models import JournalAccessSubscriptionPeriod

from core.subscription.restriction.conf import settings as restriction_settings
from core.subscription.restriction.models import (
    Abonne,
    Ipabonne,
    Ipabonneinterval,
    Revue,
    Revueabonne,
)


class ImportException(Exception):
    pass


created_objects = {
    "subscription": 0,
    "user": 0,
    "period": 0,
    "iprange": 0,
}


@transaction.atomic
def delete_stale_subscriptions(year: int, logger: structlog.BoundLogger, organisation_id=None):
    """Update stale subscription for the given year

    A stale subscription is a subscriptions that exists in the eruditorg database
    but does not exist in the restriction database. When an organisation is unsubscribed,
    the corresponding rows in revueabonne are not updated, they are simply deleted.

    This function will determine the set of subscriptions present in eruditorg, the
    set of subscriptions present in restriction, and diff them to find the set of
    subscriptions that are present in eruditorg but not in restriction. It will then
    update them to delete all their journals and subscription periods.

    :param year: the year for which stale subscriptions should be deleted
    :param logger: the logger to use
    :param organisation_id: limit deleting stale subscriptions of a specific organisation
    """

    # Get all Revueabonne for the given year.
    abonneid_for_year = (
        Revueabonne.objects.filter(anneeabonnement=year)
        .order_by("abonneid")
        .values_list("abonneid", flat=True)
        .distinct()
    )

    orgs_with_no_revueabonne = Organisation.objects.exclude(account_id__in=set(abonneid_for_year))

    # Get all organisations that have a valid subscription
    orgs_with_valid_subscription = Organisation.objects.filter(
        pk__in=JournalAccessSubscription.valid_objects.institutional()
        .values_list("organisation", flat=True)
        .distinct()
    )

    if organisation_id is not None:
        orgs_with_valid_subscription = orgs_with_valid_subscription.filter(
            account_id=organisation_id
        )

    # diff the sets and find the subscribers with no revueabonne
    orgs_with_subscription_and_no_revueabonne = orgs_with_valid_subscription.filter(
        pk__in=[o.pk for o in orgs_with_no_revueabonne]
    )

    # get their subscriptions
    stale_subscriptions = set(
        JournalAccessSubscription.valid_objects.institutional().filter(
            organisation__in=orgs_with_subscription_and_no_revueabonne
        )
    )

    # Delete their periods
    nowd = dt.datetime.now()
    JournalAccessSubscriptionPeriod.objects.filter(
        subscription__in=stale_subscriptions,
        start__lte=nowd,
        end__gte=nowd,
    ).delete()

    for subscription in stale_subscriptions:
        logger.info(
            "subscription.stale_subscription_deleted",
            subscription_pk=subscription.pk,
            organisation=subscription.organisation.name,
        )
        subscription.journals.clear()
        subscription.save()


class DryRun(transaction.Atomic):
    def __init__(self, using=None, savepoint=True, dry_run=False):
        super().__init__(using, savepoint, durable=False)
        self.dry_run = dry_run

    def __enter__(self):
        super().__enter__()

    def __exit__(self, exc_type, exc_value, traceback):
        if self.dry_run:
            transaction.set_rollback(True)
        super().__exit__(exc_type, exc_value, traceback)


class Command(BaseCommand):
    """ Import restrictions from the restriction database """

    help = 'Import data from the "restriction" database'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.created_subscriptions = set()

    def add_arguments(self, parser):
        parser.add_argument(
            "--organisation-id",
            action="store",
            dest="organisation_id",
            help="id of the organisation to import",
        )

        parser.add_argument(
            "--dry-run",
            action="store_true",
            dest="dry_run",
            help="run in dry run mode",
            default=False,
        )

        parser.add_argument(
            "--year",
            action="store",
            dest="year",
            help="year to import",
            type=int,
            default=dt.datetime.now().year,
        )

    def handle(self, *args, **options):
        organisation_id = options.get("organisation_id", None)
        year = options.get("year")
        dry_run = options.get("dry_run")

        logger = structlog.get_logger(__name__)
        if dry_run:
            logger = logger.bind(dry_run=dry_run)

        restriction_subscriptions = Revueabonne.objects.filter(anneeabonnement=year)

        if organisation_id:
            restriction_subscriptions = restriction_subscriptions.filter(abonneid=organisation_id)

        restriction_subscriber_ids = (
            restriction_subscriptions.order_by("abonneid")
            .values_list("abonneid", flat=True)
            .distinct()
        )

        logger.info(
            "import.started", import_type="restrictions", to_process=len(restriction_subscriber_ids)
        )

        with DryRun(dry_run=dry_run):
            for subscriber_id in restriction_subscriber_ids:
                # Fetches the subscriber
                try:
                    subscriber = Abonne.objects.get(pk=subscriber_id)
                except Abonne.DoesNotExist:
                    logger.error("Abonne.DoesNotExist", abonne_id=subscriber_id)
                    raise ImportException
                subscription_qs = restriction_subscriptions.filter(abonneid=subscriber_id)
                try:
                    self.import_restriction_subscriber(subscriber, subscription_qs, logger=logger)
                except ImportException:
                    pass

            delete_stale_subscriptions(year, logger, organisation_id=organisation_id)
            logger.info("import.finished", **created_objects)

    @transaction.atomic
    def import_restriction_subscriber(
        self, restriction_subscriber: Abonne, subscription_qs, logger=None
    ):

        if not logger:
            logger = structlog.get_logger(__name__)
        logger = logger.bind(subscriber_id=restriction_subscriber.pk)

        if not restriction_subscriber.courriel:
            logger.warning(
                "import_restriction_subscriber", msg="Cannot import subscriber with empty email"
            )
            return

        try:
            organisation, created = Organisation.objects.get_or_create(
                account_id=restriction_subscriber.pk
            )
            organisation.name = restriction_subscriber.abonne
            organisation.sushi_requester_id = restriction_subscriber.requesterid
            organisation.account_id = restriction_subscriber.pk
            organisation.save()

            if created:
                logger.info("organisation.created", pk=organisation.pk, name=organisation.name)
        finally:
            organisation.save()

        # gets or creates the RestrictionProfile instance
        # --

        try:
            restriction_profile = LegacyAccountProfile.objects.filter(
                origin=LegacyAccountProfile.DB_RESTRICTION
            ).get(legacy_id=str(restriction_subscriber.pk))
            user = restriction_profile.user
            user.email = restriction_subscriber.courriel
            user.save()
        except LegacyAccountProfile.DoesNotExist:
            username = "restriction-{}".format(restriction_subscriber.pk)
            user, created = get_or_create_legacy_user(
                username=username, email=restriction_subscriber.courriel
            )
            if created:
                created_objects["user"] += 1
                logger.info(
                    "user.created",
                    pk=user.pk,
                    username=username,
                    email=restriction_subscriber.courriel,
                )

            restriction_profile = LegacyAccountProfile.objects.create(
                origin=LegacyAccountProfile.DB_RESTRICTION,
                legacy_id=str(restriction_subscriber.pk),
                user=user,
                organisation=organisation,
            )

            if restriction_subscriber.icone:
                f = open(
                    op.join(restriction_settings.ABONNE_ICONS_PATH, restriction_subscriber.icone),
                    "rb",
                )
                image_file = File(f)
                organisation.badge.save(restriction_subscriber.icone, image_file, save=True)
                organisation.save()
                f.close()
        finally:
            organisation.members.add(user)
            organisation.save()
        # Delete all subscriptions for this subscriber!
        #
        # Why can we do this? Because this import script is the *only* source of subscription
        # information. Because of this, we can happily go ahead with a "delete and repopulate"
        # approach. If we don't delete our stuff, subscription deletions in Victor won't properly
        # be imported: subscription will stay here forever.

        # failsafe to ensure that we don't mistakenly delete subscriptions that aren't institutional
        if restriction_profile.organisation is None:
            raise ValidationError("Organisation is required")

        try:
            subscription = JournalAccessSubscription.objects.filter(
                organisation=restriction_profile.organisation
            ).get()
            subscription.journals.clear()
            subscription.journalaccesssubscriptionperiod_set.all().delete()
            subscription.institutionipaddressrange_set.all().delete()
        except JournalAccessSubscription.DoesNotExist:
            pass

        for subscription in subscription_qs.all():
            self.import_restriction_subscription(
                subscription, restriction_subscriber, restriction_profile, logger=logger
            )

    def import_restriction_subscription(
        self, restriction_subscription, restriction_subscriber, restriction_profile, logger=None
    ):
        if not logger:
            logger = structlog.get_logger(__name__)
        logger = logger.bind(
            subscriber_id=restriction_subscriber.pk, subscription_id=restriction_subscription.pk
        )

        #
        # Fetch the related journal
        try:
            restriction_journal = Revue.objects.get(revueid=restriction_subscription.revueid)
        except Revue.DoesNotExist:
            logger.error("Revue.DoesNotExist", revue_id=restriction_subscription.revueid)
            return

        # gets or creates a JournalAccessSubscription instance
        # --
        with sentry_sdk.configure_scope() as scope:
            scope.fingerprint = ["Journal.DoesNotExist"]

        try:
            journal_code = restriction_journal.titrerevabr.lower()
            journal = Journal.legacy_objects.get_by_id(journal_code)
        except Journal.DoesNotExist:
            logger.error("Journal.DoesNotExist", titrerevabr=restriction_journal.titrerevabr)
            return

        subscription, subscription_created = JournalAccessSubscription.objects.get_or_create(
            organisation=restriction_profile.organisation
        )
        logger = logger.bind(subscription_pk=subscription.pk)
        if subscription_created:
            created_objects["subscription"] += 1
            logger.info("subscription.created")
        if not subscription.journals.filter(pk=journal.pk):
            subscription.journals.add(journal)
            logger.info("subscription.add_journal", journal_pk=journal.pk)

        # creates the subscription period
        # --
        if subscription.pk not in self.created_subscriptions:
            self.created_subscriptions.add(subscription.pk)
            start_date = dt.date(restriction_subscription.anneeabonnement, 1, 1)
            end_date = dt.date(restriction_subscription.anneeabonnement + 1, 1, 1)
            subscription_period, created = JournalAccessSubscriptionPeriod.objects.get_or_create(
                subscription=subscription, start=start_date, end=end_date
            )

            if created:
                created_objects["period"] += 1
                logger.info(
                    "subscriptionperiod.created",
                    pk=subscription_period.pk,
                    start=start_date,
                    end=end_date,
                )

            try:
                subscription_period.clean()
            except ValidationError:
                # We are saving multiple periods for multiple journals under the same subscription
                # instance so period validation errors can happen.
                logger.error("subscriptionperiod.validationerror")
                raise
            else:
                subscription_period.save()

            # create the subscription referer
            # --

            subscription.referer = restriction_subscriber.referer
            subscription.save()

            # creates the IP whitelist associated with the subscription
            # --

            restriction_subscriber_ips_set1 = Ipabonne.objects.filter(
                abonneid=str(restriction_subscriber.pk)
            )
            for ip in restriction_subscriber_ips_set1:
                ip_start, ip_end = get_ip_range_from_ip(ip.ip)
                ip_range, created = InstitutionIPAddressRange.objects.get_or_create(
                    subscription=subscription, ip_start=ip_start, ip_end=ip_end
                )
                if created:
                    created_objects["iprange"] += 1
                    logger.info("ipabonne.created", ip_start=ip_start, ip_end=ip_end)

            restriction_subscriber_ips_ranges = Ipabonneinterval.objects.filter(
                abonneid=restriction_subscriber.pk
            )
            for ip_range in restriction_subscriber_ips_ranges:
                ip_start = get_ip(ip_range.debutinterval, repl="0")
                ip_end = get_ip(ip_range.fininterval, repl="255")
                ip_range, created = InstitutionIPAddressRange.objects.get_or_create(
                    subscription=subscription, ip_start=ip_start, ip_end=ip_end
                )
                if created:
                    created_objects["iprange"] += 1
                    logger.info("ipabonneinterval.created", ip_start=ip_start, ip_end=ip_end)


def get_ip_range_from_ip(ip):
    if "*" not in ip:
        return ip, ip
    return get_ip(ip, repl="0"), get_ip(ip, repl="255")


def get_ip(ip, repl="0"):
    ipl = ip.split(".")
    ipl_new = [repl if n == "*" else n for n in ipl]
    return ".".join(ipl_new)
