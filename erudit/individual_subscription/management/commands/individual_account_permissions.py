from erudit.models import Journal

from django.core.management.base import BaseCommand

from ...models import OrganizationPolicy, IndividualAccountJournal


class Command(BaseCommand):

    def _add_permission(self, accounts, journals):
        for account in accounts:
            for journal in journals:
                rule, created = IndividualAccountJournal.objects.get_or_create(
                    account=account,
                    journal=journal)
                if created:
                    log = '{} {}'.format(account, journal)
                    if self.verbosity > 1:
                        self.stdout.write(log)

    def handle(self, *args, **options):
        self.verbosity = int(options['verbosity'])
        organisations = OrganizationPolicy.objects.all()
        for organisation in organisations:
            accounts = organisation.accounts.all()

            if organisation.access_full:
                journals = Journal.objects.all()
                self._add_permission(accounts, journals)
