from datetime import datetime

from django.contrib.contenttypes.models import ContentType

from erudit.tests import BaseEruditTestCase
from core.permissions.models import Rule

from ..models import IssueSubmission


class BaseEditorTestCase(BaseEruditTestCase):

    def setUp(self):
        super().setUp()

        self.issue_submission = IssueSubmission.objects.create(
            journal=self.journal,
            volume="2",
            date_created=datetime.now(),
            contact=self.user,
        )

        self.other_issue_submission = IssueSubmission.objects.create(
            journal=self.other_journal,
            volume="2",
            date_created=datetime.now(),
            contact=self.user,
        )

        ct = ContentType.objects.get(app_label="erudit", model="journal")
        Rule.objects.create(content_type=ct,
                            user=self.user,
                            object_id=self.journal.id,
                            permission="editor.manage_issuesubmission")
