# -*- coding: utf-8 -*-

import datetime as dt

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q

from core.accounts.models import RestrictionProfile
from core.subscription.models import JournalAccessSubscription
from core.subscription.models import JournalAccessSubscriptionPeriod
from erudit.models import Journal
from erudit.models import Organisation

from .restriction_models import Abonne
from .restriction_models import Revue
from .restriction_models import Revueabonne


class ImportException(Exception):
    pass


class Command(BaseCommand):
    args = '<action:import_restriction>'
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
                username='restriction-user-{0}'.format(restriction_subscriber.pk),
                email=restriction_subscriber.courriel)
            organisation = Organisation.objects.create(name=restriction_subscriber.abonne[:120])
            restriction_profile = RestrictionProfile.objects.create(
                restriction_id=restriction_subscriber.pk,
                password=restriction_subscriber.motdepasse, user=user, organisation=organisation)

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
            organisation=restriction_profile.organisation, journal=journal)

        # STEP 3: creates the subscription period
        # --

        subscription_period = JournalAccessSubscriptionPeriod(
            subscription=subscription,
            start=dt.date(restriction_subscription.anneeabonnement, 2, 1),
            end=dt.date(restriction_subscription.anneeabonnement + 1, 2, 1))

        try:
            subscription_period.clean()
        except ValidationError:
            self.stdout.write(self.style.ERROR(
                '  Unable to create subscription period for RevueAbonne ID: {0}'.format(
                    restriction_subscription.pk)))
            raise ImportException

        subscription_period.save()

        self.stdout.write(self.style.MIGRATE_SUCCESS('  [OK]'))
