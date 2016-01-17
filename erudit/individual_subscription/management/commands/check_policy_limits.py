from django.core.management.base import BaseCommand

from ...models import Policy


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.verbosity = int(options['verbosity'])
        policies = Policy.objects.all()
        for policy in policies:
            policy.notify_limit_reached()
