import logging
from datetime import datetime

from django.core.management.base import BaseCommand
from django.db import connections

from erudit.models import Journal

from core.accounts.models import LegacyAccountProfile
from core.subscription.models import JournalAccessSubscription, JournalManagementSubscription
from core.accounts.shortcuts import get_or_create_legacy_user
from erudit.models import Organisation

from core.subscription.legacy.legacy_models import Abonneindividus

logger = logging.getLogger(__name__)


class Command(BaseCommand):

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
        logger.info("Individual subscriptions import started on {}".format(datetime.now()))
        for abonne in Abonneindividus.objects.all():
            try:
                profile = LegacyAccountProfile.objects.get(
                    origin=LegacyAccountProfile.DB_ABONNEMENTS,
                    legacy_id=str(abonne.abonneindividusid))
                logger.info("Account {} exists. Updating subscriptions.".format(abonne.courriel))
                user = profile.user
            except LegacyAccountProfile.DoesNotExist:
                user, created = get_or_create_legacy_user(
                    username='abonne-{}'.format(abonne.abonneindividusid),
                    email=abonne.courriel,
                )

                user.first_name = abonne.prenom
                user.last_name = abonne.nom
                user.save()
                user_creation_count += 1
                profile = LegacyAccountProfile.objects.create(
                    origin=LegacyAccountProfile.DB_ABONNEMENTS, user=user,
                    legacy_id=str(abonne.abonneindividusid))
                logger.info("User created: {} {}".format(user.username, user.email))

            sql = "SELECT revueID FROM revueindividus \
    WHERE abonneIndividusID = {}".format(profile.legacy_id)

            cursor = connections['legacy_subscription'].cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            journal_ids = [jid[0] for jid in rows]

            for journal_id in journal_ids:
                sql = "SELECT titrerevabr FROM revue WHERE revueid = {}".format(journal_id)
                cursor = connections['legacy_subscription'].cursor()
                cursor.execute(sql)
                rows = cursor.fetchall()
                titrerevabr = rows[0][0]
                if not titrerevabr:
                    continue
                try:
                    journal = Journal.legacy_objects.get_by_id(titrerevabr)
                except Journal.DoesNotExist:
                    logger.warning("Journal {} does not exists".format(titrerevabr))
                    continue

                try:
                    if JournalAccessSubscription.objects.filter(
                        user=profile.user,
                        journals=journal
                    ).exists():
                        logger.debug("Subscription exists: user={}, journal={}".format(profile.user, journal))
                        continue

                    organisation_subscription = False
                    for organisation in self.organisations:
                        if profile.user.email in self.organisations[organisation]:
                            organisation, _ = Organisation.objects.get_or_create(name=organisation)
                            access, created = JournalAccessSubscription.objects.get_or_create(
                                user=profile.user,
                                organisation=organisation
                            )
                            if created:
                                logger.info("Created for organisation: {}".format(organisation))
                                subscription_count += 1
                    if not organisation_subscription:
                        journal_sub = JournalManagementSubscription.objects.get(journal=journal)
                        access, created = JournalAccessSubscription.objects.get_or_create(
                            user=profile.user,
                            journal_management_subscription=journal_sub
                        )
                    access.journals.add(journal)
                    access.save()
                    logger.info("Importing subscription: user={}, journal={}".format(profile.user, journal))
                except JournalManagementSubscription.DoesNotExist:
                    logger.debug("No plan for Journal {}".format(journal))

        logger.info("Finished. {} users created, {} subscriptions added.".format(
            user_creation_count,
            subscription_count)
        )
