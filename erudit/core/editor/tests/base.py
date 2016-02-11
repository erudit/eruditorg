from datetime import datetime
from erudit.tests import BaseEruditTestCase

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
