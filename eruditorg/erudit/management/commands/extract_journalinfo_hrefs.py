import re

from django.core.management.base import BaseCommand

from ...models import JournalInformation


class Command(BaseCommand):
    def handle(self, *args, **options):
        FIELDS = ["about", "editorial_policy", "subscriptions", "team", "contact", "partners"]
        RE_HREF = re.compile(r'href="(http[^"]+)"')
        for info in JournalInformation.objects.all():
            for fieldname in FIELDS:
                text = getattr(info, fieldname) or ""
                for href in RE_HREF.findall(text):
                    print("{}/{}: {}".format(info.journal.code, fieldname, href))
