import pytest

from erudit.models import (
    Collection,
    Issue,
    Journal,
)
from erudit.test.factories import (
    CollectionFactory,
    IssueFactory,
    JournalFactory,
)

pytestmark = pytest.mark.django_db


class TestJournalUpcomingManager:
    def test_journals_with_no_issues_are_upcoming(self):
        journal_1 = JournalFactory()
        journals = Journal.upcoming_objects.all()
        assert list(journals) == [journal_1]

    def test_journals_with_published_issues_are_not_upcoming(self):
        JournalFactory.create_with_issue()
        journals = Journal.upcoming_objects.all()
        assert list(journals) == []

    def test_external_journals_with_unpublished_issues_are_not_upcoming(self):
        JournalFactory(redirect_to_external_url=True)
        journal_1 = JournalFactory(redirect_to_external_url=True)
        IssueFactory(journal=journal_1, is_published=False)
        assert list(Journal.upcoming_objects.all()) == []

    def test_journals_with_published_and_unpublished_issues_are_not_upcoming(self):
        journal_1 = JournalFactory.create_with_issue()
        IssueFactory(journal=journal_1, is_published=False)
        assert list(Journal.upcoming_objects.all()) == []

    def test_journals_with_unpublished_issues_are_upcoming(self):
        journal_1 = JournalFactory()
        IssueFactory(journal=journal_1, is_published=False)
        journals = Journal.upcoming_objects.all()
        assert list(journals) == [journal_1]


class TestInternalJournalManager:
    def test_returns_only_the_internal_journals(self):
        journal_1 = JournalFactory.create(
            external_url="http://example.com", redirect_to_external_url=True
        )
        JournalFactory.create()
        journals = Journal.internal_objects.all()
        assert journal_1 not in journals


class TestLegacyJournalManager:
    def test_can_return_a_journal_using_its_localidentifier_or_its_code(self):
        journal = JournalFactory.create(localidentifier="foobar42", code="foobar")
        assert Journal.legacy_objects.get_by_id("foobar") == journal
        assert Journal.legacy_objects.get_by_id("foobar42") == journal


class TestInternalIssueManager:
    def test_returns_only_the_internal_issues(self):
        issue_1 = IssueFactory.create(external_url=None)
        issue_2 = IssueFactory.create(journal=issue_1.journal, external_url="http://example.com")
        issues = Issue.internal_objects.all()
        assert issue_1 in issues
        assert issue_2 not in issues


class TestJournalCollectionManager:
    def test_returns_only_collections_associated_with_journals(self):
        collection_1 = CollectionFactory()
        collection_2 = CollectionFactory()
        CollectionFactory()
        CollectionFactory()
        JournalFactory(collection=collection_1)
        JournalFactory(collection=collection_2)
        assert list(Collection.journal_collections.all()) == [collection_1, collection_2]
