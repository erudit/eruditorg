from django.core.management.base import BaseCommand

from .legacy_models import Abonneindividus
from ..models import IndividualAccount
from ..factories import OrganizationPolicyFactory


class Command(BaseCommand):
    args = '<action:total_abonnes|list_abonnes|import_abonnes>'
    help = 'Import data from legacy system'

    def handle(self, *args, **options):
        """
        Command dispatcher
        """
        if len(args) == 0:
            self.stdout.write(self.args)
            return

        command = args[0]
        self.stdout.write(command)
        cmd = getattr(self, command)
        cmd()

    def list_abonnes(self):
        for abonne in Abonneindividus.objects.all():
            self.stdout.write(abonne.courriel)

    def total_abonnes(self):
        self.stdout.write(str(Abonneindividus.objects.count()))

    def import_abonnes(self):
        if IndividualAccount.objects.count() > 0:
            self.stdout.write("Some accounts are already present on destination \
                table. Importation canceled.")
            return

        dummy_organization_policy = OrganizationPolicyFactory()
        self.stdout.write("Dummy policy organization and its policy was created \
            to allow creation in the new system. Don't forget to remove one.")

        for old_abonne in Abonneindividus.objects.all():
            new_account = IndividualAccount(
                organization_policy=dummy_organization_policy,
                id=old_abonne.abonneindividusid,
                email=old_abonne.courriel,
                firstname=old_abonne.prenom,
                lastname=old_abonne.nom,
                password=old_abonne.password)
            new_account.save()
