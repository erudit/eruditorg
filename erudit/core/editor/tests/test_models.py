from django.test import TestCase

from ..factories import IssueSubmissionFactory
from ..models import IssueSubmission


class IssueSubmissionTestCase(TestCase):

    def test_version(self):
        issue = IssueSubmissionFactory()
        copy = issue.save_version()
        self.assertEqual(issue.journal, copy.journal)
        self.assertEqual(issue.contact, copy.contact)
        self.assertEqual(issue.date_created, copy.date_created)
        self.assertNotEqual(issue.date_modified, copy.date_modified)
        self.assertNotEqual(issue.id, copy.id)
        self.assertEqual(issue.parent, copy)

    def test_knows_if_it_is_submitted(self):
        # Setup
        issue_1 = IssueSubmissionFactory.create()
        issue_2 = IssueSubmissionFactory.create()
        issue_2.submit()
        # Run & check
        self.assertFalse(issue_1.is_submitted)
        self.assertTrue(issue_2.is_submitted)


class IssueSubmissionWorkflowTestCase(TestCase):

    def test_refuse(self):
        issue = IssueSubmissionFactory()
        issue.submit()
        issue.refuse()

        issues = IssueSubmission.objects.all().order_by('id')
        self.assertEqual(issues.count(), 2)
        self.assertEqual(issues[0].parent, issues[1])
