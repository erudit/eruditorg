import mock
from erudit.admin import IssueAdmin
from erudit.models import Issue
from erudit.test import BaseEruditTestCase
from erudit.test.factories import IssueFactory


class TestIssueAdmin(BaseEruditTestCase):

    def setUp(self):
        self.admin = IssueAdmin
        super(TestIssueAdmin, self).setUp()

    def test_can_mark_issues_as_published(self):
        # Setup
        issue_1 = IssueFactory.create(journal=self.journal, is_published=False)
        issue_2 = IssueFactory.create(journal=self.journal, is_published=False)
        issue_3 = IssueFactory.create(journal=self.journal, is_published=False)
        queryset = Issue.objects.filter(id__in=(issue_1.id, issue_2.id, ))
        # Run
        self.admin.make_published(self.admin, mock.MagicMock(), queryset)
        issue_1 = Issue.objects.get(id=issue_1.id)
        issue_2 = Issue.objects.get(id=issue_2.id)
        issue_3 = Issue.objects.get(id=issue_3.id)
        self.assertTrue(issue_1.is_published)
        self.assertTrue(issue_2.is_published)
        self.assertFalse(issue_3.is_published)

    def test_can_mark_issues_as_unpublished(self):
        # Setup
        issue_1 = IssueFactory.create(journal=self.journal, is_published=True)
        issue_2 = IssueFactory.create(journal=self.journal, is_published=True)
        issue_3 = IssueFactory.create(journal=self.journal, is_published=True)
        queryset = Issue.objects.filter(id__in=(issue_1.id, issue_2.id, ))
        # Run
        self.admin.make_unpublished(self.admin, mock.MagicMock(), queryset)
        issue_1 = Issue.objects.get(id=issue_1.id)
        issue_2 = Issue.objects.get(id=issue_2.id)
        issue_3 = Issue.objects.get(id=issue_3.id)
        self.assertFalse(issue_1.is_published)
        self.assertFalse(issue_2.is_published)
        self.assertTrue(issue_3.is_published)

    def test_can_mark_issues_force_free_access_to_true(self):
        # Setup
        issue_1 = IssueFactory.create(journal=self.journal, force_free_access=False)
        issue_2 = IssueFactory.create(journal=self.journal, force_free_access=False)
        issue_3 = IssueFactory.create(journal=self.journal, force_free_access=False)
        queryset = Issue.objects.filter(id__in=(issue_1.id, issue_2.id, ))
        # Run
        self.admin.force_free_access_to_true(self.admin, mock.MagicMock(), queryset)
        issue_1 = Issue.objects.get(id=issue_1.id)
        issue_2 = Issue.objects.get(id=issue_2.id)
        issue_3 = Issue.objects.get(id=issue_3.id)
        self.assertTrue(issue_1.force_free_access)
        self.assertTrue(issue_2.force_free_access)
        self.assertFalse(issue_3.force_free_access)

    def test_can_mark_issues_force_free_access_to_false(self):
        # Setup
        issue_1 = IssueFactory.create(journal=self.journal, force_free_access=True)
        issue_2 = IssueFactory.create(journal=self.journal, force_free_access=True)
        issue_3 = IssueFactory.create(journal=self.journal, force_free_access=True)
        queryset = Issue.objects.filter(id__in=(issue_1.id, issue_2.id, ))
        # Run
        self.admin.force_free_access_to_false(self.admin, mock.MagicMock(), queryset)
        issue_1 = Issue.objects.get(id=issue_1.id)
        issue_2 = Issue.objects.get(id=issue_2.id)
        issue_3 = Issue.objects.get(id=issue_3.id)
        self.assertFalse(issue_1.force_free_access)
        self.assertFalse(issue_2.force_free_access)
        self.assertTrue(issue_3.force_free_access)
