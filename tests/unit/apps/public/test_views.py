import pytest

from erudit.test.factories import IssueFactory, JournalFactory
from apps.public.views import HomeView


@pytest.mark.django_db
class TestHomeView:

    def test_latest_issues_order(self):
        journal_1 = JournalFactory()
        journal_2 = JournalFactory()
        issue_1 = IssueFactory(journal=journal_2)
        issue_2 = IssueFactory(journal=journal_1)
        issue_3 = IssueFactory(journal=journal_2)
        issue_4 = IssueFactory(journal=journal_1)
        issue_5 = IssueFactory(journal=journal_2)
        view = HomeView()
        context = view.get_context_data()
        # Make sure that issues from one journal published on the same
        # day as other issues from another journal are not mixed.
        assert list(context['latest_issues']) == [
            issue_2,
            issue_4,
            issue_1,
            issue_3,
            issue_5,
        ]
