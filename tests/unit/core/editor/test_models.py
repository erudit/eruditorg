import pytest
from resumable_uploads.models import ResumableFile

from base.test.factories import GroupFactory, UserFactory
from core.editor.models import IssueSubmission, ProductionTeam
from core.editor.test.factories import IssueSubmissionFactory, ProductionTeamFactory


pytestmark = pytest.mark.django_db


class TestIssueSubmission:
    def test_version(self):
        issue = IssueSubmissionFactory.create()
        new_files_version = issue.save_version()
        assert issue.files_versions.count() == 2
        assert issue.last_files_version == new_files_version

    def test_knows_if_it_is_a_draft(self):
        issue_1 = IssueSubmissionFactory.create()
        issue_2 = IssueSubmissionFactory.create()
        issue_2.submit()
        assert issue_1.is_draft
        assert not issue_2.is_draft

    def test_knows_if_it_is_submitted(self):
        issue_1 = IssueSubmissionFactory.create()
        issue_2 = IssueSubmissionFactory.create()
        issue_2.submit()
        assert not issue_1.is_submitted
        assert issue_2.is_submitted

    def test_knows_if_it_needs_corrections(self):
        issue_1 = IssueSubmissionFactory()
        issue_2 = IssueSubmissionFactory()
        issue_1.submit()
        issue_1.refuse()
        assert issue_1.needs_corrections
        assert not issue_2.needs_corrections

    def test_knows_if_it_is_validated(self):
        issue_1 = IssueSubmissionFactory.create()
        issue_2 = IssueSubmissionFactory.create()
        issue_2.submit()
        issue_2.approve()
        assert not issue_1.is_validated
        assert issue_2.is_validated

    def test_can_remove_incomplete_files_during_submission(self):
        issue = IssueSubmissionFactory.create()
        rfile = ResumableFile.objects.create(path="dummy/path.png", filesize=42, uploadsize=10)
        issue.last_files_version.submissions.add(rfile)
        issue.submit()
        assert issue.files_versions.count() == 1
        assert issue.files_versions.all()[0].submissions.count() == 0


class TestIssueSubmissionWorkflow:
    def test_refuse(self):
        issue = IssueSubmissionFactory()
        issue.submit()
        issue.refuse()

        issues = IssueSubmission.objects.all().order_by("id")
        assert issues.count() == 1
        assert issues.first().files_versions.count() == 2


class TestProductionTeam:
    def test_load(self):
        production_team = ProductionTeamFactory()
        assert ProductionTeam.load() == production_team

    def test_emails(self):
        group = GroupFactory()
        ProductionTeamFactory(group=group)
        user = UserFactory(email="foo@bar.com")
        user.groups.add(group)
        assert ProductionTeam.emails() == ["foo@bar.com"]
