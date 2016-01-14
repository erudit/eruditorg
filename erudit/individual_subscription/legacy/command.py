import csv
import os

from django.core.management.base import BaseCommand
from django.db import connections
from django.contrib.contenttypes.models import ContentType

from erudit.models import Journal, Organisation
from erudit.factories import OrganisationFactory

from .legacy_models import Abonneindividus
from ..models import IndividualAccount, Policy
from ..factories import PolicyFactory


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

        dummy_organization_policy = PolicyFactory(content_object=OrganisationFactory())
        self.stdout.write("Dummy policy organization and its policy was created \
            to allow creation in the new system. Don't forget to remove one.")

        for old_abonne in Abonneindividus.objects.all():
            new_account = IndividualAccount(
                policy=dummy_organization_policy,
                id=old_abonne.abonneindividusid,
                email=old_abonne.courriel,
                firstname=old_abonne.prenom,
                lastname=old_abonne.nom,
                password=old_abonne.password)
            new_account.save()

    def link_abonnes_from_csv(self):
        # Create policy from filename if it does not exist
        filename = self.args[1]
        basename = os.path.basename(filename)
        if '.' in basename:
            basename = basename.split('.')[0]
        organization = Organisation.objects.get(name__iexact=basename)
        policy = Policy(content_object=organization)
        policy.save()
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
                    account.policy = policy
                    account.save()
                except Exception:
                    print('{} {}'.format('account', email))

                # Define the journal in the policy

                if isinstance(journal_id, int) and \
                        Journal.objects.filter(id=journal_id).count() == 1:
                    journal = Journal.objects.get(id=journal_id)
                    policy.access_journal.add(journal)
                    policy.save()

    def link_abonnes_from_acces(self):
        dummy_policy_id = self.args[1]
        accounts = IndividualAccount.objects.filter(policy_id=dummy_policy_id)
        cursor = connections['legacy_individual_subscription'].cursor()

        journals_account_volumetry = {"": []}

        for account in accounts:
            cursor.execute("SELECT revueID FROM Revueindividus WHERE abonneIndividusID = {}".format(account.id))
            publishers = []
            journals = []
            rows = cursor.fetchall()

            if len(rows) == 0:
                journals_account_volumetry[""].append(account)

            for row in rows:
                try:
                    journal = Journal.objects.get(id=row[0])
                    journals.append(journal)
                    publishers.append(journal.publisher)
                except Journal.DoesNotExist:
                    publishers.append("XXX No revue {}".format(row[0]))

                jids = sorted([j.id for j in journals])
                key = "|".join([str(j) for j in jids])
                if key not in journals_account_volumetry:
                    journals_account_volumetry[key] = []
                journals_account_volumetry[key].append(account)

        for k, accounts in journals_account_volumetry.items():
            # Not any access
            if k is '':
                for account in accounts:
                    account.active = False
                    account.save()

            # Journal policy
            if k is not '' and len(k.split('|')) == 1 and len(accounts) > 1:
                journal = Journal.objects.get(id=k)
                policy = Policy(content_object=journal)
                policy.save()
                policy.access_journal.add(journal)
                policy.save()
                for account in accounts:
                    account.policy = policy
                    account.save()

            # Individual policy
            if k is not '' and len(accounts) == 1:
                account = accounts[0]
                ids = k.split('|')
                journals = Journal.objects.filter(id__in=ids)
                ct = ContentType.objects.get(app_label=account._meta.app_label, model=account.__class__.__name__.lower())
                if Policy.objects.filter(content_type=ct, object_id=account.id).count():
                    policy = Policy.objects.get(content_type=ct, object_id=account.id)
                else:
                    policy = Policy(content_object=account)
                    policy.save()
                for journal in journals:
                    policy.access_journal.add(journal)
                policy.save()

                account.policy = policy
                account.save()
