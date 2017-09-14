import logging
import itertools
from datetime import datetime

from django.core.management.base import BaseCommand
from django.db import connections

from erudit.models import Journal

from core.accounts.models import LegacyAccountProfile
from core.subscription.models import JournalAccessSubscription, JournalManagementSubscription
from django.contrib.auth.models import User
from erudit.models import Organisation

from core.subscription.legacy.legacy_models import Abonneindividus

logger = logging.getLogger(__name__)


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
        return JournalAccessSubscription.objects.filter(
            user=user,
            journals=journal
        ).exists()

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
                logger.info("Created for organisation: {}".format(organisation))
                return access, created
        return None, False

    def _get_or_create_journal_management_subscription(self, user, journal):
        journal_sub = JournalManagementSubscription.objects.get(journal=journal)
        access, created = JournalAccessSubscription.objects.get_or_create(
            user=user,
            journal_management_subscription=journal_sub
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
        logger.info("Individual subscriptions import started on {}".format(datetime.now()))
        for abonne in Abonneindividus.objects.all():
            try:
                profile = LegacyAccountProfile.objects.get(
                    origin=LegacyAccountProfile.DB_ABONNEMENTS,
                    legacy_id=str(abonne.abonneindividusid))
                user = profile.user
            except LegacyAccountProfile.DoesNotExist:
                try:
                    user = User.objects.get(
                        username='abonne-{}'.format(
                            abonne.abonneindividusid
                        ),
                        email=abonne.courriel
                    )
                except User.DoesNotExist:
                    user = User(
                        username='abonne-{}'.format(abonne.abonneindividusid),
                        email=abonne.courriel,
                    )

                    user.first_name = abonne.prenom
                    user.last_name = abonne.nom

            sql = "SELECT revueID FROM revueindividus \
 WHERE abonneIndividusID = {}".format(abonne.abonneindividusid)

            cursor = connections['legacy_subscription'].cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            journal_ids = [jid[0] for jid in rows]

            for revueid in journal_ids:
                try:
                    journal = self._get_journal_for_revueid(revueid)
                    if self._user_is_subscribed_to_journal(user, journal):
                        logger.debug(
                            "Subscription exists: user={}, journal={}".format(user, journal)
                        )
                        continue

                    email_in_org_list = self._email_in_organisation_list(user.email)
                    can_create_subscription = self._can_create_journal_subscription(journal)

                    # Only save the user if we are going to create a subscription
                    if not user.pk and (email_in_org_list or can_create_subscription):
                        user.save()
                        user_creation_count += 1
                        profile = LegacyAccountProfile.objects.create(
                            origin=LegacyAccountProfile.DB_ABONNEMENTS, user=user,
                            legacy_id=str(abonne.abonneindividusid))
                        logger.info("User created: {} {}".format(user.username, user.email))
                    elif (not email_in_org_list and not can_create_subscription):
                        continue
                    else:
                        logger.debug("Account {} exists. Updating subscriptions.".format(user.pk))

                    access, created = self._get_or_create_organisation_subscription(
                        profile.user, journal
                    )
                    if created:
                        subscription_count += 1
                    elif not access or not access.pk:
                        access, created = self._get_or_create_journal_management_subscription(
                            profile.user, journal
                        )
                        if created:
                            subscription_count += 1
                    access.journals.add(journal)
                    access.save()
                    logger.info("Importing subscription: user={}, journal={}".format(
                        profile.user, journal
                    ))

                except Journal.DoesNotExist:
                    continue

                except JournalManagementSubscription.DoesNotExist:
                    logger.debug("No plan for Journal {}".format(journal))

        logger.info("Finished. {} users created, {} subscriptions added.".format(
            user_creation_count,
            subscription_count)
        )
