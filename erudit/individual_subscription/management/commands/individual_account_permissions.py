from erudit.models import Journal

from django.core.management.base import BaseCommand

from ...models import OrganizationPolicy, IndividualAccountJournal


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.verbosity = int(options['verbosity'])
        organisations = OrganizationPolicy.objects.all()
        for organisation in organisations:
            organisation.generate_flat_access()
