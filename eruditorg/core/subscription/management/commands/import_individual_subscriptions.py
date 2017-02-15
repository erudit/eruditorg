import logging
from datetime import datetime

from django.core.management.base import BaseCommand
from django.db import connections

from erudit.models import Journal

from core.accounts.hashers import PBKDF2WrappedAbonnementsSHA1PasswordHasher
from core.accounts.models import LegacyAccountProfile
from core.subscription.models import JournalAccessSubscription
from core.accounts.shortcuts import get_or_create_legacy_user

from core.subscription.legacy.legacy_models import Abonneindividus

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **options):
        """
        Command dispatcher
        """
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
                hasher = PBKDF2WrappedAbonnementsSHA1PasswordHasher()
                user, created = get_or_create_legacy_user(
                    username='abonne-{}'.format(abonne.abonneindividusid),
                    email=abonne.courriel,
                    hashed_password=hasher.encode_sha1_hash(abonne.password, hasher.salt()))
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
            cursor = connections['abonnement'].cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            journal_ids = [jid[0] for jid in rows]
            access, _ = JournalAccessSubscription.objects.get_or_create(
                user=profile.user
            )

            journals = Journal.objects.filter(
                id__in=journal_ids
            ).exclude(id__in=access.journals.all())

            if journals.count():
                logger.info("Importing {} subscriptions for {}".format(
                    journals.count(), user.username
                ))
            else:
                logger.debug("No new subscriptions to import for {}".format(user.username))
            subscription_count += journals.count()
            for j in journals:
                access.journals.add(j)
            access.save()
        logger.info("Finished. {} users created, {} subscriptions added.".format(
            user_creation_count,
            subscription_count)
        )
