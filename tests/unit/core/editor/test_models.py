# -* coding: utf-8 -*-

from base.test.testcases import EruditTestCase

from core.editor.models import IssueSubmission
from core.editor.test.factories import IssueSubmissionFactory


class TestIssueSubmission(EruditTestCase):

    def test_version(self):
        issue = IssueSubmissionFactory.create(journal=self.journal)
        new_files_version = issue.save_version()
        assert issue.files_versions.count() == 2
        assert issue.last_files_version == new_files_version

    def test_knows_if_it_is_a_draft(self):
        # Setup
        issue_1 = IssueSubmissionFactory.create(journal=self.journal)
        issue_2 = IssueSubmissionFactory.create(journal=self.journal)
        issue_2.submit()
        # Run & check
        assert issue_1.is_draft
        assert not issue_2.is_draft

    def test_knows_if_it_is_submitted(self):
        # Setup
        issue_1 = IssueSubmissionFactory.create(journal=self.journal)
        issue_2 = IssueSubmissionFactory.create(journal=self.journal)
        issue_2.submit()
        # Run & check
        assert not issue_1.is_submitted
        assert issue_2.is_submitted

    def test_knows_if_it_is_validated(self):
        # Setup
        issue_1 = IssueSubmissionFactory.create(journal=self.journal)
        issue_2 = IssueSubmissionFactory.create(journal=self.journal)
        issue_2.submit()
        issue_2.approve()
        # Run & check
        assert not issue_1.is_validated
        assert issue_2.is_validated

    def test_knows_if_it_is_archived(self):
        # Setup
        issue_1 = IssueSubmissionFactory.create(journal=self.journal)
        issue_2 = IssueSubmissionFactory.create(journal=self.journal)
        issue_2.submit()
        issue_2.approve()
        issue_2.archive()
        # Run & check
        assert not issue_1.is_archived
        assert issue_2.is_archived


class TestIssueSubmissionWorkflow(EruditTestCase):
    def test_refuse(self):
        issue = IssueSubmissionFactory(journal=self.journal)
        issue.submit()
        issue.refuse()

        issues = IssueSubmission.objects.all().order_by('id')
        assert issues.count() == 1
        assert issues.first().files_versions.count() == 2
