from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from base.test.factories import UserFactory
from erudit.test.factories import JournalFactory

from core.authorization.defaults import AuthorizationConfig as AC
from core.authorization.models import Authorization

from ..models import IssueSubmission


class BaseEditorTestCase(TestCase):

    def setUp(self):
        self.user = UserFactory()

        # Add a journal with a member
        self.journal = JournalFactory()
        self.journal.members.add(self.user)

        self.issue_submission = IssueSubmission.objects.create(
            journal=self.journal,
            volume="2",
            contact=self.user,
        )

        ct = ContentType.objects.get(app_label="erudit", model="journal")
        Authorization.objects.create(
            content_type=ct,
            user=self.user,
            object_id=self.journal.id,
            authorization_codename=AC.can_manage_issuesubmission.codename)
