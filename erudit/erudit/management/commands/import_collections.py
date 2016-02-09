from datetime import datetime

from django.core.management.base import BaseCommand
from erudit.models.core import Collection
from erudit.utils.edinum import fetch_collections_from_edinum


class Command(BaseCommand):

    help = """Import issues from edinum"""

    def handle(self, *args, **options):

        for (coll_id, coll_name) in fetch_collections_from_edinum():
            coll = Collection()
            coll.edinum_id = coll_id
            coll.name = coll_name
            coll.synced_with_edinum = True
            coll.sync_date = datetime.now()
            if coll_id == 4:
                coll.code = 'unb'
            if coll_id == 1:
                coll.code = 'erudit'
            coll.save()
