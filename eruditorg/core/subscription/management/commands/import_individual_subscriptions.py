from django.core.management.base import BaseCommand

from core.accounts.hashers import PBKDF2WrappedAbonnementsSHA1PasswordHasher
from core.accounts.models import LegacyAccountProfile
from core.accounts.shortcuts import get_or_create_legacy_user

from core.subscription.legacy.legacy_models import Abonneindividus


class Command(BaseCommand):
    args = '<action:total_abonnes|list_abonnes|import_abonnes>'
    help = 'Import data from legacy system'

    def handle(self, *args, **options):
        """
        Command dispatcher
        """
        self.stdout.write(self.style.MIGRATE_HEADING("Importing legacy accounts"))
        for old_abonne in Abonneindividus.objects.all():
            try:
                account = LegacyAccountProfile.objects.get(
                    origin=LegacyAccountProfile.DB_ABONNEMENTS,
                    legacy_id=str(old_abonne.abonneindividusid))
                self.stdout.write("Account {} already exists".format(old_abonne.abonneindividusid))
            except LegacyAccountProfile.DoesNotExist:
                self.stdout.write("Importing user {}".format(old_abonne.abonneindividusid))
                hasher = PBKDF2WrappedAbonnementsSHA1PasswordHasher()
                user = get_or_create_legacy_user(
                    username='abonne-{}'.format(old_abonne.abonneindividusid),
                    email=old_abonne.courriel,
                    hashed_password=hasher.encode_sha1_hash(old_abonne.password, hasher.salt()))
                user.first_name = old_abonne.prenom
                user.last_name = old_abonne.nom
                user.save()
                LegacyAccountProfile.objects.create(
                    origin=LegacyAccountProfile.DB_ABONNEMENTS, user=user,
                    legacy_id=str(old_abonne.abonneindividusid))
                self.stdout.write(self.style.SUCCESS('  [OK]'))

