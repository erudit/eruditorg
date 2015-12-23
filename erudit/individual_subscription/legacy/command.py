import csv
import os

from django.core.management.base import BaseCommand

from erudit.models import Journal, Organisation

from .legacy_models import Abonneindividus
from ..models import IndividualAccount, OrganizationPolicy
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

        self.args = args
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

    def link_abonnes(self):
        # Create policy from filename if it does not exist
        filename = self.args[1]
        basename = os.path.basename(filename)
        if '.' in basename:
            basename = basename.split('.')[0]
        organization = Organisation.objects.get(name__iexact=basename)
        policy, created = OrganizationPolicy.objects.get_or_create(organization=organization)
        print(policy)

        with open(filename, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                email = row[2]
                journal_id = row[3]

                # Assign the policy to the account
                try:
                    account = IndividualAccount.objects.\
                        get(email__iexact=email)
                    account.organization_policy = policy
                    account.save()
                except Exception:
                    print('{} {}'.format('account', email))

                # Define the journal in the policy

                if isinstance(journal_id, int) and \
                        Journal.objects.filter(id=journal_id).count() == 1:
                    journal = Journal.objects.get(id=journal_id)
                    policy.access_journal.add(journal)
                    policy.save()
