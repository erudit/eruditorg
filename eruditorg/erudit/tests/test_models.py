# -*- coding: utf-8 -*-

import datetime as dt

from eruditarticle.objects import EruditJournal
from eruditarticle.objects import EruditPublication

from erudit.fedora.objects import JournalDigitalObject
from erudit.fedora.objects import PublicationDigitalObject
from erudit.factories import ArticleFactory
from erudit.factories import AuthorFactory
from erudit.factories import IssueFactory
from erudit.factories import JournalFactory
from erudit.factories import JournalTypeFactory

from .base import BaseEruditTestCase


class TestJournal(BaseEruditTestCase):
    def test_can_return_the_associated_eulfedora_model(self):
        # Run & check
        self.assertEqual(self.journal.fedora_model, JournalDigitalObject)

    def test_can_return_the_associated_erudit_class(self):
        # Run & check
        self.assertEqual(self.journal.erudit_class, EruditJournal)

    def test_can_return_an_appropriate_fedora_pid(self):
        # Setup
        self.journal.localidentifier = 'dummy139'
        self.journal.save()
        # Run & check
        self.assertEqual(self.journal.pid, 'erudit:erudit.dummy139')

    def test_can_return_its_published_issues(self):
        # Setup
        issue_1 = IssueFactory.create(
            journal=self.journal, date_published=dt.datetime.now() - dt.timedelta(days=1))
        issue_2 = IssueFactory.create(journal=self.journal, date_published=dt.datetime.now())
        IssueFactory.create(
            journal=self.journal, date_published=dt.datetime.now() + dt.timedelta(days=30))
        # Run & check
        self.assertEqual(set(self.journal.published_issues), {issue_1, issue_2})

    def test_can_return_its_first_issue(self):
        # Setup
        issue_1 = IssueFactory.create(
            journal=self.journal, date_published=dt.datetime.now() - dt.timedelta(days=1))
        IssueFactory.create(journal=self.journal, date_published=dt.datetime.now())
        IssueFactory.create(
            journal=self.journal, date_published=dt.datetime.now() + dt.timedelta(days=30))
        # Run & check
        self.assertEqual(self.journal.first_issue, issue_1)

    def test_can_return_its_last_issue(self):
        # Setup
        IssueFactory.create(
            journal=self.journal, date_published=dt.datetime.now() - dt.timedelta(days=1))
        issue_2 = IssueFactory.create(journal=self.journal, date_published=dt.datetime.now())
        IssueFactory.create(
            journal=self.journal, date_published=dt.datetime.now() + dt.timedelta(days=30))
        # Run & check
        self.assertEqual(self.journal.last_issue, issue_2)

    def test_can_return_its_last_issue_with_open_access(self):
        # Setup
        IssueFactory.create(
            journal=self.journal, date_published=dt.datetime.now() - dt.timedelta(days=2))
        issue_2 = IssueFactory.create(
            journal=self.journal, date_published=dt.datetime.now() - dt.timedelta(days=1),
            open_access=True)
        IssueFactory.create(
            journal=self.journal, date_published=dt.datetime.now(), open_access=False)
        IssueFactory.create(
            journal=self.journal, date_published=dt.datetime.now() + dt.timedelta(days=30),
            open_access=True)
        # Run & check
        self.assertEqual(self.journal.last_oa_issue, issue_2)

    def test_knows_if_it_is_provided_by_fedora(self):
        # Run & check
        self.journal.localidentifier = 'dummy139'
        self.journal.save()
        self.assertTrue(self.journal.provided_by_fedora)
        self.journal.localidentifier = None
        self.journal.save()
        self.assertFalse(self.journal.provided_by_fedora)

    def test_can_return_its_letter_prefix(self):
        # Setup
        journal_1 = JournalFactory.create(
            name='Test', collection=self.collection, publishers=[self.publisher])
        journal_2 = JournalFactory.create(
            name=None, collection=self.collection, publishers=[self.publisher])
        # Run & check
        self.assertEqual(journal_1.letter_prefix, 'T')
        self.assertIsNone(journal_2.letter_prefix)


class TestIssue(BaseEruditTestCase):
    def setUp(self):
        super(TestIssue, self).setUp()
        self.issue = IssueFactory.create(journal=self.journal)

    def test_can_return_the_associated_eulfedora_model(self):
        # Run & check
        self.assertEqual(self.issue.fedora_model, PublicationDigitalObject)

    def test_can_return_the_associated_erudit_class(self):
        # Run & check
        self.assertEqual(self.issue.erudit_class, EruditPublication)

    def test_can_return_its_full_identifier(self):
        # Setup
        self.journal.localidentifier = 'dummy139'
        self.journal.save()
        self.issue.localidentifier = 'dummy1234'
        self.issue.save()
        # Run & check
        self.assertEqual(self.issue.get_full_identifier(), 'erudit:erudit.dummy139.dummy1234')

    def test_can_return_an_appropriate_fedora_pid(self):
        # Setup
        self.journal.localidentifier = 'dummy139'
        self.journal.save()
        self.issue.localidentifier = 'dummy1234'
        self.issue.save()
        # Run & check
        self.assertEqual(self.issue.pid, 'erudit:erudit.dummy139.dummy1234')

    def test_knows_if_it_has_a_movable_limitation_in_case_of_scientific_journals(self):
        # Setup
        now_dt = dt.datetime.now()
        self.journal.type = JournalTypeFactory.create(code='S')
        self.journal.save()
        issue_1 = IssueFactory.create(
            journal=self.journal, open_access=False,
            date_published=dt.date(now_dt.year - 3, 3, 20))
        issue_2 = IssueFactory.create(
            journal=self.journal, open_access=False,
            date_published=dt.date(now_dt.year - 1, 3, 20))
        issue_3 = IssueFactory.create(
            journal=self.journal, open_access=False,
            date_published=dt.date(now_dt.year - 5, 3, 20))
        # Run & check
        self.assertTrue(issue_1.has_movable_limitation)
        self.assertTrue(issue_2.has_movable_limitation)
        self.assertFalse(issue_3.has_movable_limitation)

    def test_knows_if_it_has_a_movable_limitation_in_case_of_non_scientific_journals(self):
        # Setup
        now_dt = dt.datetime.now()
        self.journal.type = JournalTypeFactory.create(code='C')
        self.journal.save()
        issue_1 = IssueFactory.create(
            journal=self.journal, open_access=False,
            date_published=dt.date(now_dt.year - 3, 3, 20))
        issue_2 = IssueFactory.create(
            journal=self.journal, open_access=False,
            date_published=dt.date(now_dt.year - 1, 3, 20))
        issue_3 = IssueFactory.create(
            journal=self.journal, open_access=False,
            date_published=dt.date(now_dt.year - 5, 3, 20))
        # Run & check
        self.assertFalse(issue_1.has_movable_limitation)
        self.assertTrue(issue_2.has_movable_limitation)
        self.assertFalse(issue_3.has_movable_limitation)

    def test_knows_that_issues_with_open_access_has_no_movable_limitation(self):
        # Setup
        now_dt = dt.datetime.now()
        self.journal.type = JournalTypeFactory.create(code='C')
        self.journal.save()
        issue_1 = IssueFactory.create(
            journal=self.journal, open_access=True,
            date_published=dt.date(now_dt.year - 3, 3, 20))
        issue_2 = IssueFactory.create(
            journal=self.journal, open_access=True,
            date_published=dt.date(now_dt.year - 1, 3, 20))
        issue_3 = IssueFactory.create(
            journal=self.journal, open_access=None,
            date_published=dt.date(now_dt.year - 5, 3, 20))
        # Run & check
        self.assertFalse(issue_1.has_movable_limitation)
        self.assertFalse(issue_2.has_movable_limitation)
        self.assertFalse(issue_3.has_movable_limitation)


class TestArticle(BaseEruditTestCase):

    def setUp(self):
        super(TestArticle, self).setUp()
        self.issue = IssueFactory.create(journal=self.journal)
        self.article = ArticleFactory.create(issue=self.issue)

    def test_knows_that_it_is_in_open_access_if_its_issue_is_in_open_access(self):
        # Setup
        issue_1 = IssueFactory.create(journal=self.journal, open_access=True)
        article_1 = ArticleFactory.create(issue=issue_1)
        issue_2 = IssueFactory.create(journal=self.journal, open_access=False)
        article_2 = ArticleFactory.create(issue=issue_2)
        # Run 1 check
        self.assertTrue(article_1.open_access)
        self.assertFalse(article_2.open_access)

    def test_knows_if_it_is_in_open_access_if_its_journal_is_in_open_access(self):
        # Setup
        self.journal.open_access = True
        self.journal.save()
        issue_1 = IssueFactory.create(journal=self.journal, open_access=None)
        article_1 = ArticleFactory.create(issue=issue_1)
        issue_2 = IssueFactory.create(journal=self.journal, open_access=False)
        article_2 = ArticleFactory.create(issue=issue_2)
        # Run 1 check
        self.assertTrue(article_1.open_access)
        self.assertFalse(article_2.open_access)

    def test_knows_if_it_has_a_movable_limitation(self):
        # Setup
        now_dt = dt.datetime.now()
        self.journal.type = JournalTypeFactory.create(code='S')
        self.journal.save()
        issue_1 = IssueFactory.create(
            journal=self.journal, open_access=False,
            date_published=dt.date(now_dt.year - 3, 3, 20))
        issue_2 = IssueFactory.create(
            journal=self.journal, open_access=False,
            date_published=dt.date(now_dt.year - 1, 3, 20))
        issue_3 = IssueFactory.create(
            journal=self.journal, open_access=False,
            date_published=dt.date(now_dt.year - 5, 3, 20))
        article_1 = ArticleFactory.create(issue=issue_1)
        article_2 = ArticleFactory.create(issue=issue_2)
        article_3 = ArticleFactory.create(issue=issue_3)
        # Run & check
        self.assertTrue(article_1.has_movable_limitation)
        self.assertTrue(article_2.has_movable_limitation)
        self.assertFalse(article_3.has_movable_limitation)


class TestAuthor(BaseEruditTestCase):
    def test_can_return_articles_written_for_a_given_journal(self):
        # Setup
        other_journal = JournalFactory.create(
            collection=self.collection, publishers=[self.publisher])
        other_issue = IssueFactory.create(
            journal=other_journal, date_published=dt.datetime.now())
        other_article = ArticleFactory.create(issue=other_issue)

        issue = IssueFactory.create(
            journal=self.journal, date_published=dt.datetime.now())
        article = ArticleFactory.create(issue=issue)

        author = AuthorFactory.create()

        article.authors.add(author)
        other_article.authors.add(author)

        # Run
        self.assertEqual(list(author.articles_in_journal(self.journal)), [article, ])
