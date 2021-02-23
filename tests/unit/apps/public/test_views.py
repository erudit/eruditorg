import datetime
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
        assert context["latest_issues"] == {
            issue_2.localidentifier: [issue_2],
            issue_4.localidentifier: [issue_4],
            issue_1.localidentifier: [issue_1],
            issue_3.localidentifier: [issue_3],
            issue_5.localidentifier: [issue_5],
        }

    def test_latest_issues_with_retrospective_issues_grouping(self):
        journal = JournalFactory()

        # Current year issue.
        issue_1 = IssueFactory(journal=journal, year=datetime.datetime.now().year)
        # Retrospective issue.
        issue_2 = IssueFactory(journal=journal, year=2000)
        # Retrospective issue.
        issue_3 = IssueFactory(journal=journal, year=2001)
        # Last year issue.
        issue_4 = IssueFactory(journal=journal, year=datetime.datetime.now().year - 1)
        # Retrospective issue.
        issue_5 = IssueFactory(journal=journal, year=2002)

        view = HomeView()
        context = view.get_context_data()

        # Make sure that retrospective issues (older than last year) are grouped together.
        assert context["latest_issues"] == {
            issue_1.localidentifier: [issue_1],
            journal.localidentifier: [issue_2, issue_3, issue_5],
            issue_4.localidentifier: [issue_4],
        }
