import structlog

import itertools
from datetime import datetime

from django.core.management.base import BaseCommand
from django.db import connections

from erudit.models import Journal

from core.accounts.models import LegacyAccountProfile
from core.subscription.models import (
    JournalAccessSubscription, JournalManagementSubscription, JournalAccessSubscriptionPeriod
)
from django.contrib.auth.models import User
from erudit.models import Organisation

from core.subscription.legacy.legacy_models import Abonneindividus

logger = structlog.get_logger(__name__)

import_date = datetime.now()
end_date = datetime(month=12, day=31, year=2017)


class Command(BaseCommand):

    def _get_journal_for_revueid(self, revueid):
        sql = "SELECT titrerevabr FROM revue WHERE revueid = {}".format(revueid)
        cursor = connections['legacy_subscription'].cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        titrerevabr = rows[0][0]
        if not titrerevabr:
            raise Journal.DoesNotExist
        try:
            return Journal.legacy_objects.get_by_id(titrerevabr)
        except Journal.DoesNotExist:
            logger.warning("Journal {} does not exists".format(titrerevabr))
            raise

    def _user_is_subscribed_to_journal(self, user, journal):

        is_subscribed = JournalAccessSubscription.objects.filter(
            user=user,
            journals=journal
        ).exists()
        return is_subscribed

    def _email_in_organisation_list(self, email):
        return email in set(itertools.chain.from_iterable(self.organisations.values()))

    def _can_create_journal_subscription(self, journal):
        return JournalManagementSubscription.objects.filter(journal=journal).exists()

    def _get_or_create_organisation_subscription(self, user, journal):
        for organisation in self.organisations:
            if user.email in self.organisations[organisation]:
                organisation, _ = Organisation.objects.get_or_create(name=organisation)
                access, created = JournalAccessSubscription.objects.get_or_create(
                    user=user,
                    sponsor=organisation
                )
                access.journalaccesssubscriptionperiod_set.all().delete()
                JournalAccessSubscriptionPeriod.objects.get_or_create(
                    subscription=access,
                    start=import_date,
                    end=end_date
                )

                return access, created
        return None, False

    def _get_or_create_journal_management_subscription(self, user, journal):
        journal_sub = JournalManagementSubscription.objects.get(journal=journal)
        access, created = JournalAccessSubscription.objects.get_or_create(
            user=user,
            journal_management_subscription=journal_sub
        )
        access.journalaccesssubscriptionperiod_set.all().delete()

        JournalAccessSubscriptionPeriod.objects.get_or_create(
            subscription=access,
            start=import_date,
            end=end_date
        )
        return access, created

    def add_arguments(self, parser):
        parser.add_argument(
            '--file', action="store", nargs="+", dest="files"
        )

    def handle(self, *args, **options):
        """
        Command dispatcher
        """
        self.organisations = {}
        for filename in options.get('files'):
            with open(filename, 'r', encoding="utf-8") as csv_file:
                import csv
                csvreader = csv.reader(csv_file)
                self.organisations[filename[:filename.index(".")]] = {row[0] for row in csvreader}

        user_creation_count = 0
        subscription_count = 0
        logger = structlog.get_logger(__name__)
        logger.info("import.started")

        for abonne in Abonneindividus.objects.all():
            logger = structlog.get_logger(__name__)
            try:
                profile = LegacyAccountProfile.objects.get(
                    origin=LegacyAccountProfile.DB_ABONNEMENTS,
                    legacy_id=str(abonne.abonneindividusid))
                user = profile.user
            except LegacyAccountProfile.DoesNotExist:
                try:
                    user = User.objects.get(
                        username=abonne.courriel,
                        email=abonne.courriel
                    )
                except User.DoesNotExist:
                    user = User(
                        username=abonne.courriel,
                        email=abonne.courriel,
                    )

                    user.first_name = abonne.prenom
                    user.last_name = abonne.nom
            logger = logger.bind(email=user.email)
            sql = "SELECT revueID FROM revueindividus \
 WHERE abonneIndividusID = {}".format(abonne.abonneindividusid)

            cursor = connections['legacy_subscription'].cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            journal_ids = [jid[0] for jid in rows]

            for revueid in journal_ids:
                try:
                    logger.unbind('sponsor', 'reason')
                except KeyError:
                    pass

                logger = logger.bind(abonnement_revue_id=revueid)
                try:
                    journal = self._get_journal_for_revueid(revueid)
                    logger = logger.bind(journal=journal.code)

                    if self._user_is_subscribed_to_journal(user, journal):
                        logger.info(
                            "import.subscription", imported=False, reason="subscription.exists"
                        )
                        continue

                    # Only save the user if we are going to create a subscription
                    email_in_org_list = self._email_in_organisation_list(user.email)
                    journal_has_plan = self._can_create_journal_subscription(journal)
                    can_create_subscription = email_in_org_list or journal_has_plan

                    if not user.pk and can_create_subscription:
                        user.save()
                        user_creation_count += 1
                        profile = LegacyAccountProfile.objects.create(
                            origin=LegacyAccountProfile.DB_ABONNEMENTS, user=user,
                            legacy_id=str(abonne.abonneindividusid))
                        logger.info("user.created", email=user.email)
                    elif not can_create_subscription:
                        logger.info("import.subscription", imported=False, reason="no.plan")
                        continue

                    # We try to create an organisation subscription
                    access, created = self._get_or_create_organisation_subscription(
                        profile.user, journal
                    )
                    if created:
                        subscription_count += 1
                        logger = logger.bind(sponsor=access.sponsor.name)
                    elif access is None:
                        # If we can't create it, we create a journal subscription
                        access, created = self._get_or_create_journal_management_subscription(
                            profile.user, journal
                        )
                        if created:
                            subscription_count += 1
                            journal_sub = JournalManagementSubscription.objects.get(journal=journal)
                            logger = logger.bind(plan=journal_sub.pk)

                    access.journals.add(journal)
                    access.save()
                    logger.info("import.subscription", imported=True)

                except Journal.DoesNotExist:
                    logger.info("import.subscription", imported=False, reason="does.not.exist")
                    continue

                except JournalManagementSubscription.DoesNotExist:
                    continue

        logger.info(
            "import.finished",
            users_created=user_creation_count,
            subscriptions_created=subscription_count
        )
