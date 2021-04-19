import pytest

from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType

from base.test.factories import UserFactory
from base.test.testcases import Client
from erudit.test.factories import JournalFactory

from core.authorization.defaults import AuthorizationConfig as AC
from core.authorization.models import Authorization
from core.editor.test.factories import ProductionTeamFactory

from ..models import IssueSubmission


@pytest.mark.django_db
class BaseEditorTestCase:
    @pytest.fixture(autouse=True)
    def setup(self):
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
            authorization_codename=AC.can_manage_issuesubmission.codename,
        )

        # We need to be logged in for all the tests
        self.client = Client(logged_user=self.user)

        # Setup production team group
        self.group = Group.objects.create(name="Main production team")
        self.production_team = ProductionTeamFactory(
            group=self.group, identifier="main-production-team"
        )
        self.production_team.journals.add(self.journal)
        self.user.groups.add(self.group)
