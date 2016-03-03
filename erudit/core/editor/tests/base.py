from django.contrib.contenttypes.models import ContentType

from erudit.tests import BaseEruditTestCase
from core.permissions.models import ObjectPermission
from core.editor.rules import MANAGE_ISSUESUBMISSION

from ..models import IssueSubmission


class BaseEditorTestCase(BaseEruditTestCase):

    def setUp(self):
        super().setUp()

        self.issue_submission = IssueSubmission.objects.create(
            journal=self.journal,
            volume="2",
            contact=self.user,
        )

        self.other_issue_submission = IssueSubmission.objects.create(
            journal=self.other_journal,
            volume="2",
            contact=self.user,
        )

        ct = ContentType.objects.get(app_label="erudit", model="journal")
        ObjectPermission.objects.create(
            content_type=ct,
            user=self.user,
            object_id=self.journal.id,
            permission=MANAGE_ISSUESUBMISSION)
