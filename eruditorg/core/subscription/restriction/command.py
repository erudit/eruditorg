# -*- coding: utf-8 -*-

import datetime as dt
import os.path as op

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q
from PIL import Image

from core.accounts.models import RestrictionProfile
from core.subscription.models import InstitutionIPAddressRange
from core.subscription.models import JournalAccessSubscription
from core.subscription.models import JournalAccessSubscriptionPeriod
from erudit.models import Journal
from erudit.models import Organisation

from .conf import settings as restriction_settings
from .restriction_models import Abonne
from .restriction_models import Adressesip
from .restriction_models import Ipabonne
from .restriction_models import Ipabonneinterval
from .restriction_models import Revue
from .restriction_models import Revueabonne


class ImportException(Exception):
    pass


class Command(BaseCommand):
    args = '<action:import_restriction|check_ongoing_restrictions|gen_dummy_badges>'
    help = 'Import data from the "restriction" database'

    def handle(self, *args, **options):
        if len(args) == 0:
            self.stdout.write(self.args)
            return

        self.args = args
        command = args[0]
        self.stdout.write(command)
        cmd = getattr(self, command)
        cmd()

    def gen_dummy_badges(self):
        for abonne in Abonne.objects.all():
            if not abonne.icone:
                continue
            im = Image.frombytes('L', (100, 100), b"\x00" * 100 * 100)
            im.save(op.join(restriction_settings.ABONNE_ICONS_PATH, abonne.icone))

    def import_restriction(self):
        considered_year = dt.datetime.now().year - 1
        restriction_subscriptions = Revueabonne.objects.filter(anneeabonnement__gte=considered_year)

        self.stdout.write(self.style.MIGRATE_HEADING(
            'Start importing "restriction" subscriptions ({0} subscriptions to import!)'.format(
                restriction_subscriptions.count()
            )))

        for restriction_subscription in restriction_subscriptions:
            try:
                self._import_restriction_subscription(restriction_subscription)
            except ImportException:
                pass

    def check_ongoing_restrictions(self):
        current_year = dt.datetime.now().year
        restriction_subscriptions = Revueabonne.objects.filter(
            anneeabonnement__in=[current_year - 1, current_year, ])

        self.stdout.write(self.style.MIGRATE_HEADING(
            'Start checking {0} ongoing "restriction" subscriptions!'.format(
                restriction_subscriptions.count()
            )))

        for restriction_subscription in restriction_subscriptions:
            try:
                self.stdout.write(self.style.MIGRATE_LABEL(
                    '    Start checking the subscription with ID: {0}'.format(
                        restriction_subscription.id)),
                    ending='')
                self._check_restriction_subscription(restriction_subscription)
                self.stdout.write(self.style.MIGRATE_SUCCESS('  [OK]'))
            except AssertionError as e:
                self.stdout.write(self.style.ERROR('  {0}'.format(e.args[0])))

    @transaction.atomic
    def _import_restriction_subscription(self, restriction_subscription):
        self.stdout.write(self.style.MIGRATE_LABEL(
            '    Start importing the subscription with ID: {0}'.format(
                restriction_subscription.id)),
            ending='')

        user_model = get_user_model()

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
            restriction_profile = RestrictionProfile.objects.get(
                restriction_id=restriction_subscriber.pk)
        except RestrictionProfile.DoesNotExist:
            user = user_model.objects.create(
                username=restriction_subscriber.courriel,
                email=restriction_subscriber.courriel)
            organisation = Organisation.objects.create(name=restriction_subscriber.abonne[:120])
            restriction_profile = RestrictionProfile.objects.create(
                restriction_id=restriction_subscriber.pk,
                password=restriction_subscriber.motdepasse, user=user, organisation=organisation)

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

        subscription_period = JournalAccessSubscriptionPeriod(
            subscription=subscription,
            start=dt.date(restriction_subscription.anneeabonnement, 2, 1),
            end=dt.date(restriction_subscription.anneeabonnement + 1, 2, 1))

        try:
            subscription_period.clean()
        except ValidationError:
            # We are saving multiple periods for multiple journals under the same subscription
            # instance so period validation errors can happen.
            pass
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

        self.stdout.write(self.style.MIGRATE_SUCCESS('  [OK]'))

    def _check_restriction_subscription(self, restriction_subscription):
        # Fetches the subscriber
        restriction_subscriber = Abonne.objects.filter(pk=restriction_subscription.abonneid).first()
        assert restriction_subscriber is not None, \
            '  Unable to retrieve the "Abonne" instance with ID: {0}'.format(
                restriction_subscription.abonneid)

        # Fetches the related journal
        restriction_journal = Revue.objects.filter(revueid=restriction_subscription.revueid).first()
        assert restriction_journal is not None, \
            '  Unable to retrieve the "Revue" instance with ID: {0}'.format(
                restriction_subscription.revueid)

        # STEP 1: checks that the RestrictionProfile instance has been created
        # --

        restriction_profile = RestrictionProfile.objects.filter(
            restriction_id=restriction_subscriber.pk).first()
        assert restriction_profile is not None, \
            '  Unable to retrieve the "RestrictionProfile" instance with ' \
            'restriction_id: {0}'.format(restriction_subscriber.pk)

        # STEP 2: checks that the RestrictionProfile instance is associated with a user who is a
        # a member of an organisation that corresponds to the restriction subscriber.
        # --

        user = restriction_profile.user
        organisation = restriction_profile.organisation
        assert user.email == restriction_subscriber.courriel, \
            'Invalid email for imported user {0}'.format(user)
        assert organisation.name == restriction_subscriber.abonne[:120], \
            'Invalid name for imported organisation {0}'.format(user)

        # STEP 3: checks the JournalAccessSubscription instance related to the considered
        # restriction.
        # --

        subscription = JournalAccessSubscription.objects.filter(
            organisation=restriction_profile.organisation).first()
        assert subscription is not None, \
            'Unable to find the JournalAccessSubscription instance ' \
            'associated with the restriction (ID: {0})'.format(restriction_subscription.pk)
        journal_code = restriction_journal.titrerevabr.lower()
        journal_exists = subscription.journals \
            .filter(Q(localidentifier=journal_code) | Q(code=journal_code)).exists()
        assert journal_exists, \
            'Unable to find the journal (code: {0}) associated with the restriction ' \
            'in the journals associated with the JournalAccessSubscription ' \
            'instance (ID: {1})'.format(journal_code, restriction_subscription.pk)

        # STEP 4: checks that the subscription period is properly registered.
        # --

        dstart = dt.date(restriction_subscription.anneeabonnement, 2, 1)
        dend = dt.date(restriction_subscription.anneeabonnement + 1, 2, 1)
        period_exists = JournalAccessSubscriptionPeriod.objects.filter(
            subscription=subscription, start__lte=dstart, end__gte=dend).exists()
        assert period_exists, \
            'Unable to find a valid period associated with the JournalAccessSubscription ' \
            'instance for the restriction (ID: {0})'.format(restriction_subscription.pk)

        # STEP 5: checks that the IP associated with the restriction are whitelisted.
        # --

        restriction_subscriber_ips_set1 = Ipabonne.objects.filter(
            abonneid=str(restriction_subscriber.pk))
        for ip in restriction_subscriber_ips_set1:
            ip_start, ip_end = self._get_ip_range_from_ip(ip.ip)
            ip_range_exists = InstitutionIPAddressRange.objects.filter(
                subscription=subscription, ip_start=ip_start, ip_end=ip_end).exists()
            assert ip_range_exists, \
                'Unable to find the IP range [{0}, {1}] associated with the ' \
                'restriction (ID: {3})'.format(restriction_subscription.pk)

        restriction_subscriber_ips_set2 = Adressesip.objects.filter(
            abonneid=restriction_subscriber.pk)
        for ip in restriction_subscriber_ips_set2:
            ip_start, ip_end = self._get_ip_range_from_ip(ip.ip)
            ip_range_exists = InstitutionIPAddressRange.objects.filter(
                subscription=subscription, ip_start=ip_start, ip_end=ip_end).exists()
            assert ip_range_exists, \
                'Unable to find the IP range [{0}, {1}] associated with the ' \
                'restriction (ID: {3})'.format(restriction_subscription.pk)

        restriction_subscriber_ips_ranges = Ipabonneinterval.objects.filter(
            abonneid=restriction_subscriber.pk)
        for ip_range in restriction_subscriber_ips_ranges:
            ip_start = self._get_ip(ip_range.debutinterval, repl='0')
            ip_end = self._get_ip(ip_range.fininterval, repl='255')
            ip_range_exists = InstitutionIPAddressRange.objects.filter(
                subscription=subscription, ip_start=ip_start, ip_end=ip_end).exists()
            assert ip_range_exists, \
                'Unable to find the IP range [{0}, {1}] associated with the ' \
                'restriction (ID: {3})'.format(restriction_subscription.pk)

    def _get_ip_range_from_ip(self, ip):
        if '*' not in ip:
            return ip, ip
        return self._get_ip(ip, repl='0'), self._get_ip(ip, repl='255')

    def _get_ip(self, ip, repl='0'):
        ipl = ip.split('.')
        ipl_new = [repl if n == '*' else n for n in ipl]
        return '.'.join(ipl_new)
