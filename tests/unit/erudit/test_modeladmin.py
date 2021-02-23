from unittest import mock

import pytest
from erudit.admin import IssueAdmin
from erudit.models import Issue
from erudit.test.factories import IssueFactory

pytestmark = pytest.mark.django_db


class TestIssueAdmin:
    def test_can_mark_issues_force_free_access_to_true(self):
        # Setup
        issue_1 = IssueFactory.create(force_free_access=False)
        issue_2 = IssueFactory.create(journal=issue_1.journal, force_free_access=False)
        issue_3 = IssueFactory.create(journal=issue_1.journal, force_free_access=False)
        queryset = Issue.objects.filter(
            id__in=(
                issue_1.id,
                issue_2.id,
            )
        )
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
        queryset = Issue.objects.filter(
            id__in=(
                issue_1.id,
                issue_2.id,
            )
        )
        # Run
        IssueAdmin.force_free_access_to_false(IssueAdmin, mock.MagicMock(), queryset)
        issue_1 = Issue.objects.get(id=issue_1.id)
        issue_2 = Issue.objects.get(id=issue_2.id)
        issue_3 = Issue.objects.get(id=issue_3.id)
        assert not issue_1.force_free_access
        assert not issue_2.force_free_access
        assert issue_3.force_free_access
