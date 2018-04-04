from django.core.management.base import BaseCommand

from core.editor.tasks import _handle_issuesubmission_files_removal


class Command(BaseCommand):
    def handle(self, *args, **options):
        _handle_issuesubmission_files_removal()
