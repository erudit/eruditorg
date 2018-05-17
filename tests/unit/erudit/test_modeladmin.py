from unittest import mock

import pytest
from erudit.admin import IssueAdmin
from erudit.models import Issue
from erudit.test.factories import IssueFactory

pytestmark = pytest.mark.django_db


class TestIssueAdmin:
    def test_can_mark_issues_as_published(self):
        issue_1 = IssueFactory.create(is_published=False)
        issue_2 = IssueFactory.create(journal=issue_1.journal, is_published=False)
        issue_3 = IssueFactory.create(journal=issue_1.journal, is_published=False)
        queryset = Issue.objects.filter(id__in=(issue_1.id, issue_2.id, ))
        IssueAdmin.make_published(IssueAdmin, mock.MagicMock(), queryset)
        issue_1 = Issue.objects.get(id=issue_1.id)
        issue_2 = Issue.objects.get(id=issue_2.id)
        issue_3 = Issue.objects.get(id=issue_3.id)
        assert issue_1.is_published
        assert issue_2.is_published
        assert not issue_3.is_published

    def test_can_mark_issues_as_unpublished(self):
        issue_1 = IssueFactory.create(is_published=True)
        issue_2 = IssueFactory.create(journal=issue_1.journal, is_published=True)
        issue_3 = IssueFactory.create(journal=issue_1.journal, is_published=True)
        queryset = Issue.objects.filter(id__in=(issue_1.id, issue_2.id, ))
        IssueAdmin.make_unpublished(IssueAdmin, mock.MagicMock(), queryset)
        issue_1 = Issue.objects.get(id=issue_1.id)
        issue_2 = Issue.objects.get(id=issue_2.id)
        issue_3 = Issue.objects.get(id=issue_3.id)
        assert not issue_1.is_published
        assert not issue_2.is_published
        assert issue_3.is_published

    def test_can_mark_issues_force_free_access_to_true(self):
        # Setup
        issue_1 = IssueFactory.create(force_free_access=False)
        issue_2 = IssueFactory.create(journal=issue_1.journal, force_free_access=False)
        issue_3 = IssueFactory.create(journal=issue_1.journal, force_free_access=False)
        queryset = Issue.objects.filter(id__in=(issue_1.id, issue_2.id, ))
        # Run
        IssueAdmin.force_free_access_to_true(IssueAdmin, mock.MagicMock(), queryset)
        issue_1 = Issue.objects.get(id=issue_1.id)
        issue_2 = Issue.objects.get(id=issue_2.id)
        issue_3 = Issue.objects.get(id=issue_3.id)
        assert issue_1.force_free_access
        assert issue_2.force_free_access
        assert not issue_3.force_free_access

    def test_can_mark_issues_force_free_access_to_false(self):
        # Setup
        issue_1 = IssueFactory.create(force_free_access=True)
        issue_2 = IssueFactory.create(journal=issue_1.journal, force_free_access=True)
        issue_3 = IssueFactory.create(journal=issue_1.journal, force_free_access=True)
        queryset = Issue.objects.filter(id__in=(issue_1.id, issue_2.id, ))
        # Run
        IssueAdmin.force_free_access_to_false(IssueAdmin, mock.MagicMock(), queryset)
        issue_1 = Issue.objects.get(id=issue_1.id)
        issue_2 = Issue.objects.get(id=issue_2.id)
        issue_3 = Issue.objects.get(id=issue_3.id)
        assert not issue_1.force_free_access
        assert not issue_2.force_free_access
        assert issue_3.force_free_access
