from django.core.management.base import BaseCommand

from core.editor.tasks import _handle_issue_submission_action_needed


class Command(BaseCommand):
    def handle(self, *args, **options):
        _handle_issue_submission_action_needed()
