from django.core.management.base import BaseCommand

from core.citations.models import SavedCitation
from apps.public.search.models import Generic


class Command(BaseCommand):
    def handle(self, *args, **options):
        qs = SavedCitation.objects
        print("Checking {} citations...".format(qs.count()))
        for citation in qs.all():
            solr_id = citation.solr_id
            print(solr_id)
            Generic.from_solr_id(solr_id)  # no crash
        print("Done!")
