# -* coding: utf-8 -*-

from erudit.tests import BaseEruditTestCase

from ..factories import IssueSubmissionFactory
from ..models import IssueSubmission


class IssueSubmissionTestCase(BaseEruditTestCase):

    def test_version(self):
        issue = IssueSubmissionFactory.create(journal=self.journal)
        new_files_version = issue.save_version()
        self.assertEqual(issue.files_versions.count(), 2)
        self.assertEqual(issue.last_files_version, new_files_version)

    def test_knows_if_it_is_submitted(self):
        # Setup
        issue_1 = IssueSubmissionFactory.create(journal=self.journal)
        issue_2 = IssueSubmissionFactory.create(journal=self.journal)
        issue_2.submit()
        # Run & check
        self.assertFalse(issue_1.is_submitted)
        self.assertTrue(issue_2.is_submitted)


class IssueSubmissionWorkflowTestCase(BaseEruditTestCase):

    def test_refuse(self):
        issue = IssueSubmissionFactory(journal=self.journal)
        issue.submit()
        issue.refuse()

        issues = IssueSubmission.objects.all().order_by('id')
        self.assertEqual(issues.count(), 1)
        self.assertEqual(issues.first().files_versions.count(), 2)
