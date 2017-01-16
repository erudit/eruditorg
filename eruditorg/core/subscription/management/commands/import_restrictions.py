# -*- coding: utf-8 -*-

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
from core.subscription.restriction.restriction_models import (
    Abonne,
    Adressesip,
    Ipabonne,
    Ipabonneinterval,
    Revue,
    Revueabonne,
)


class ImportException(Exception):
    pass


class Command(BaseCommand):
    """ Import restrictions from the restriction database """
    help = 'Import data from the "restriction" database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--organisation-id', action='store', dest='organisation_id',
            help="id of the organisation to import"
        )

        parser.add_argument(
            '--year', action='store', dest='year', help="year to import", type=int,
            default=dt.datetime.now().year
        )

    def handle(self, *args, **options):
        self.organisation_id = options.get('organisation_id', None)
        self.year = options.get('year')

        restriction_subscriptions = Revueabonne.objects.filter(anneeabonnement__gte=self.year)

        if self.organisation_id:
            restriction_subscriptions = restriction_subscriptions.filter(
                abonneid=self.organisation_id
            )

        self.stdout.write(self.style.MIGRATE_HEADING(
            'Start importing "restriction" subscriptions ({0} subscriptions to import!)'.format(
                restriction_subscriptions.count()
            )))

        for restriction_subscription in restriction_subscriptions:
            try:
                self._import_restriction_subscription(restriction_subscription)
            except ImportException:
                pass

    @transaction.atomic
    def _import_restriction_subscription(self, restriction_subscription):
        self.stdout.write(self.style.MIGRATE_LABEL(
            '    Start importing the subscription with ID: {0}'.format(
                restriction_subscription.id)),
            ending='')

        # Fetches the subscriber
        try:
            restriction_subscriber = Abonne.objects.get(pk=restriction_subscription.abonneid)
        except Abonne.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                '  Unable to retrieve the "Abonne" instance with ID: {0}'.format(
                    restriction_subscription.abonneid)))
            raise ImportException

        # Fetch the related journal
        try:
            restriction_journal = Revue.objects.get(revueid=restriction_subscription.revueid)
        except Revue.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                '  Unable to retrieve the "Revue" instance with ID: {0}'.format(
                    restriction_subscription.revueid)))
            raise ImportException

        # STEP 1: gets or creates the RestrictionProfile instance
        # --

        try:
            restriction_profile = LegacyAccountProfile.objects \
                .filter(origin=LegacyAccountProfile.DB_RESTRICTION) \
                .get(legacy_id=str(restriction_subscriber.pk))
        except LegacyAccountProfile.DoesNotExist:
            user = get_or_create_legacy_user(
                username='restriction-{}'.format(restriction_subscriber.pk),
                email=restriction_subscriber.courriel)
            organisation = Organisation.objects.create(name=restriction_subscriber.abonne[:120])
            restriction_profile = LegacyAccountProfile.objects.create(
                origin=LegacyAccountProfile.DB_RESTRICTION,
                legacy_id=str(restriction_subscriber.pk),
                user=user, organisation=organisation)

            if restriction_subscriber.icone:
                f = open(
                    op.join(restriction_settings.ABONNE_ICONS_PATH, restriction_subscriber.icone),
                    'rb')
                image_file = File(f)
                organisation.badge.save(restriction_subscriber.icone, image_file, save=True)
                organisation.save()
                f.close()

        # STEP 2: gets or creates a JournalAccessSubscription instance
        # --

        try:
            journal_code = restriction_journal.titrerevabr.lower()
            journal = Journal.objects.get(Q(localidentifier=journal_code) | Q(code=journal_code))
        except Journal.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                '  Unable to retrieve the "Journal" instance with code: {0}'.format(
                    restriction_journal.titrerevabr)))
            raise ImportException

        subscription, _ = JournalAccessSubscription.objects.get_or_create(
            organisation=restriction_profile.organisation)
        subscription.journals.add(journal)

        # STEP 3: creates the subscription period
        # --

        subscription_period, _ = JournalAccessSubscriptionPeriod.objects.get_or_create(
            subscription=subscription,
            start=dt.date(restriction_subscription.anneeabonnement, 2, 1),
            end=dt.date(restriction_subscription.anneeabonnement + 1, 2, 1))

        try:
            subscription_period.clean()
        except ValidationError as ve:
            # We are saving multiple periods for multiple journals under the same subscription
            # instance so period validation errors can happen.
            self.stdout.write(self.style.ERROR(
                ' Cannot save the subscription period : {0}'.format(
                    ve)))
            raise
        else:
            subscription_period.save()

        # STEP 4: creates the IP whitelist associated with the subscription
        # --

        restriction_subscriber_ips_set1 = Ipabonne.objects.filter(
            abonneid=str(restriction_subscriber.pk))
        for ip in restriction_subscriber_ips_set1:
            ip_start, ip_end = self._get_ip_range_from_ip(ip.ip)
            InstitutionIPAddressRange.objects.get_or_create(
                subscription=subscription, ip_start=ip_start, ip_end=ip_end)

        restriction_subscriber_ips_set2 = Adressesip.objects.filter(
            abonneid=restriction_subscriber.pk)
        for ip in restriction_subscriber_ips_set2:
            ip_start, ip_end = self._get_ip_range_from_ip(ip.ip)
            InstitutionIPAddressRange.objects.get_or_create(
                subscription=subscription, ip_start=ip_start, ip_end=ip_end)

        restriction_subscriber_ips_ranges = Ipabonneinterval.objects.filter(
            abonneid=restriction_subscriber.pk)
        for ip_range in restriction_subscriber_ips_ranges:
            ip_start = self._get_ip(ip_range.debutinterval, repl='0')
            ip_end = self._get_ip(ip_range.fininterval, repl='255')
            InstitutionIPAddressRange.objects.get_or_create(
                subscription=subscription, ip_start=ip_start, ip_end=ip_end)

        self.stdout.write(self.style.SUCCESS('  [OK]'))

    def _get_ip_range_from_ip(self, ip):
        if '*' not in ip:
            return ip, ip
        return self._get_ip(ip, repl='0'), self._get_ip(ip, repl='255')

    def _get_ip(self, ip, repl='0'):
        ipl = ip.split('.')
        ipl_new = [repl if n == '*' else n for n in ipl]
        return '.'.join(ipl_new)
