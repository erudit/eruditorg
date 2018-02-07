# -*- coding: utf-8 -*-
import pytest

from erudit.models import Article
from erudit.models import Issue
from erudit.models import Journal
from erudit.test import BaseEruditTestCase
from erudit.test.factories import ArticleFactory
from erudit.test.factories import IssueFactory
from erudit.test.factories import JournalFactory


@pytest.mark.django_db
class TestJournalUpcomingManager(object):
    def test_journals_with_no_issues_are_upcoming(self):
        # Setup
        journal_1 = JournalFactory()
        # Run
        journals = Journal.upcoming_objects.all()
        # Check
        assert list(journals) == [journal_1]

    def test_journals_with_published_issues_are_not_upcoming(self):
        # Setup
        JournalFactory.create_with_issue()
        # Run
        journals = Journal.upcoming_objects.all()
        # Check
        assert list(journals) == []

    def test_external_journals_with_unpublished_issues_are_not_upcoming(self):
        # Setup
        JournalFactory(redirect_to_external_url=True)
        journal_1 = JournalFactory(redirect_to_external_url=True)
        IssueFactory(journal=journal_1, is_published=False)
        # Test
        assert list(Journal.upcoming_objects.all()) == []

    def test_journals_with_published_and_unpublished_issues_are_not_upcoming(self):
        # Setup
        journal_1 = JournalFactory.create_with_issue()
        IssueFactory(journal=journal_1, is_published=False)
        # Test
        assert list(Journal.upcoming_objects.all()) == []

    def test_journals_with_unpublished_issues_are_upcoming(self):
        # Setup
        journal_1 = JournalFactory()
        IssueFactory(journal=journal_1, is_published=False)
        # Test
        journals = Journal.upcoming_objects.all()
        assert list(journals) == [journal_1]


class TestInternalJournalManager(BaseEruditTestCase):
    def test_returns_only_the_internal_journals(self):
        # Setup
        journal_1 = JournalFactory.create(
            collection=self.collection,
            external_url='http://example.com',
            redirect_to_external_url=True
        )
        JournalFactory.create(collection=self.collection)
        # Run
        journals = Journal.internal_objects.all()
        # Check
        self.assertTrue(journal_1 not in journals)


class TestLegacyJournalManager(BaseEruditTestCase):
    def test_can_return_a_journal_using_its_localidentifier_or_its_code(self):
        # Setup
        journal = JournalFactory.create(
            collection=self.collection, localidentifier='foobar42', code='foobar')
        # Run & check
        self.assertEqual(Journal.legacy_objects.get_by_id('foobar'), journal)
        self.assertEqual(Journal.legacy_objects.get_by_id('foobar42'), journal)


class TestInternalIssueManager(BaseEruditTestCase):
    def test_returns_only_the_internal_issues(self):
        # Setup
        issue_1 = IssueFactory.create(journal=self.journal, external_url=None)
        issue_2 = IssueFactory.create(journal=self.journal, external_url='http://example.com')
        # Run
        issues = Issue.internal_objects.all()
        # Check
        self.assertTrue(issue_1 in issues)
        self.assertTrue(issue_2 not in issues)


class TestInternalArticleManager(BaseEruditTestCase):
    def test_returns_only_the_internal_articles(self):
        # Setup
        issue = IssueFactory.create(journal=self.journal, external_url=None)
        article_1 = ArticleFactory.create(issue=issue, external_url=None)
        article_2 = ArticleFactory.create(issue=issue, external_url='http://example.com')
        # Run
        articles = Article.internal_objects.all()
        # Check
        self.assertTrue(article_1 in articles)
        self.assertTrue(article_2 not in articles)
