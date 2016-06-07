from django.contrib.contenttypes.models import ContentType

from core.authorization.defaults import AuthorizationConfig as AC
from core.authorization.models import Authorization
from erudit.test import BaseEruditTestCase

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
        Authorization.objects.create(
            content_type=ct,
            user=self.user,
            object_id=self.journal.id,
            authorization_codename=AC.can_manage_issuesubmission.codename)
