# -*- coding: utf-8 -*-
import structlog
import datetime as dt

from django.core.management.base import BaseCommand
from django.db.models import Q

from core.accounts.models import LegacyAccountProfile
from core.subscription.models import InstitutionIPAddressRange
from core.subscription.models import JournalAccessSubscription

from core.subscription.restriction.models import (
    Abonne,
    Adressesip,
    Ipabonne,
    Ipabonneinterval,
    Revue,
    Revueabonne,
)

logger = structlog.getLogger(__name__)


class ImportException(Exception):
    pass


class Command(BaseCommand):
    help = "Check ongoing restrictions"

    def add_arguments(self, parser):
        parser.add_argument(
            "--year",
            action="store",
            dest="year",
            default=dt.datetime.now().year,
            help="Ending year of the restrictions period to check.",
        )

    def handle(self, *args, **options):
        year = int(options.get("year"))
        restriction_subscriptions = Revueabonne.objects.filter(
            anneeabonnement__in=[
                year - 1,
                year,
            ]
        )

        logger.info(
            "ongoing.restrictions.check.started", year=year, count=restriction_subscriptions.count()
        )
        for restriction_subscription in restriction_subscriptions:
            try:
                self._check_restriction_subscription(restriction_subscription)
                logger.info("subscription.check", id=restriction_subscription.id, status="OK")
            except AssertionError:
                logger.info("subscription.check", id=restriction_subscription.id, status="ERROR")

    def _check_restriction_subscription(self, restriction_subscription):
        # Fetches the subscriber
        restriction_subscriber = Abonne.objects.filter(pk=restriction_subscription.abonneid).first()
        assert (
            restriction_subscriber is not None
        ), '  Unable to retrieve the "Abonne" instance with ID: {0}'.format(
            restriction_subscription.abonneid
        )

        # Fetches the related journal
        restriction_journal = Revue.objects.filter(revueid=restriction_subscription.revueid).first()
        assert (
            restriction_journal is not None
        ), '  Unable to retrieve the "Revue" instance with ID: {0}'.format(
            restriction_subscription.revueid
        )

        # STEP 1: checks that the RestrictionProfile instance has been created
        # --

        restriction_profile = LegacyAccountProfile.objects.filter(
            origin=LegacyAccountProfile.DB_RESTRICTION, legacy_id=str(restriction_subscriber.pk)
        ).first()
        assert restriction_profile is not None, (
            '  Unable to retrieve the "RestrictionProfile" instance with '
            "restriction_id: {0}".format(restriction_subscriber.pk)
        )

        # STEP 2: checks that the RestrictionProfile instance is associated with a user who is a
        # a member of an organisation that corresponds to the restriction subscriber.
        # --

        user = restriction_profile.user
        organisation = restriction_profile.organisation
        assert (
            user.email == restriction_subscriber.courriel
        ), "Invalid email for imported user {0}".format(user)
        assert (
            organisation.name == restriction_subscriber.abonne[:120]
        ), "Invalid name for imported organisation {0}".format(user)

        # STEP 3: checks the JournalAccessSubscription instance related to the considered
        # restriction.
        # --
        subscription = JournalAccessSubscription.objects.filter(
            organisation=restriction_profile.organisation
        ).first()
        assert subscription is not None, (
            "Unable to find the JournalAccessSubscription instance "
            "associated with the restriction (ID: {0})".format(restriction_subscription.pk)
        )
        journal_code = restriction_journal.titrerevabr.lower()
        journal_exists = subscription.journals.filter(
            Q(localidentifier=journal_code) | Q(code=journal_code)
        ).exists()
        assert journal_exists, (
            "Unable to find the journal (code: {0}) associated with the restriction "
            "in the journals associated with the JournalAccessSubscription "
            "instance (ID: {1})".format(journal_code, restriction_subscription.pk)
        )

        # STEP 4: checks that the IP associated with the restriction are whitelisted.
        # --

        restriction_subscriber_ips_set1 = Ipabonne.objects.filter(
            abonneid=str(restriction_subscriber.pk)
        )
        for ip in restriction_subscriber_ips_set1:
            ip_start, ip_end = self._get_ip_range_from_ip(ip.ip)
            ip_range_exists = InstitutionIPAddressRange.objects.filter(
                subscription=subscription, ip_start=ip_start, ip_end=ip_end
            ).exists()
            assert ip_range_exists, (
                f"Unable to find the IP range [{ip_start}, {ip_end}] associated with the "
                "restriction (ID: {restriction_subscription.pk})"
            )

        restriction_subscriber_ips_set2 = Adressesip.objects.filter(
            abonneid=restriction_subscriber.pk
        )
        for ip in restriction_subscriber_ips_set2:
            ip_start, ip_end = self._get_ip_range_from_ip(ip.ip)
            ip_range_exists = InstitutionIPAddressRange.objects.filter(
                subscription=subscription, ip_start=ip_start, ip_end=ip_end
            ).exists()
            assert ip_range_exists, (
                f"Unable to find the IP range [{ip_start}, {ip_end}] associated with the "
                "restriction (ID: {restriction_subscription.pk})"
            )

        restriction_subscriber_ips_ranges = Ipabonneinterval.objects.filter(
            abonneid=restriction_subscriber.pk
        )
        for ip_range in restriction_subscriber_ips_ranges:
            ip_start = self._get_ip(ip_range.debutinterval, repl="0")
            ip_end = self._get_ip(ip_range.fininterval, repl="255")
            ip_range_exists = InstitutionIPAddressRange.objects.filter(
                subscription=subscription, ip_start=ip_start, ip_end=ip_end
            ).exists()
            assert ip_range_exists, (
                f"Unable to find the IP range [{ip_start}, {ip_end}] associated with the "
                "restriction (ID: {restriction_subscription.pk})"
            )

    def _get_ip_range_from_ip(self, ip):
        if "*" not in ip:
            return ip, ip
        return self._get_ip(ip, repl="0"), self._get_ip(ip, repl="255")

    def _get_ip(self, ip, repl="0"):
        ipl = ip.split(".")
        ipl_new = [repl if n == "*" else n for n in ipl]
        return ".".join(ipl_new)
