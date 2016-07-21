# -*- coding: utf-8 -*-

import datetime as dt
import io
import unittest.mock

from django.conf import settings
from eruditarticle.objects import EruditJournal
from eruditarticle.objects import EruditPublication

from erudit.fedora.objects import JournalDigitalObject
from erudit.fedora.objects import PublicationDigitalObject
from erudit.test import BaseEruditTestCase
from erudit.test.factories import ArticleFactory
from erudit.test.factories import AuthorFactory
from erudit.test.factories import IssueFactory
from erudit.test.factories import JournalFactory
from erudit.test.factories import JournalTypeFactory


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
        issue_1 = IssueFactory.create(journal=self.journal, year=2010)
        issue_2 = IssueFactory.create(journal=self.journal, year=2009)
        IssueFactory.create(journal=self.journal, year=dt.datetime.now().year + 2)
        # Run & check
        self.assertEqual(set(self.journal.published_issues), {issue_1, issue_2})

    def test_can_return_its_first_issue(self):
        # Setup
        issue_1 = IssueFactory.create(
            journal=self.journal, year=2010,
            date_published=dt.datetime.now() - dt.timedelta(days=1))
        IssueFactory.create(journal=self.journal, year=2010, date_published=dt.datetime.now())
        IssueFactory.create(
            journal=self.journal, year=dt.datetime.now().year + 2,
            date_published=dt.datetime.now() + dt.timedelta(days=30))
        # Run & check
        self.assertEqual(self.journal.first_issue, issue_1)

    def test_can_return_its_last_issue(self):
        # Setup
        IssueFactory.create(
            journal=self.journal, year=2010,
            date_published=dt.datetime.now() - dt.timedelta(days=1))
        issue_2 = IssueFactory.create(
            journal=self.journal, year=2010, date_published=dt.datetime.now())
        IssueFactory.create(
            journal=self.journal, year=dt.datetime.now().year + 2,
            date_published=dt.datetime.now() + dt.timedelta(days=30))
        # Run & check
        self.assertEqual(self.journal.last_issue, issue_2)

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

    def test_can_return_the_published_open_access_issues(self):
        # Setup
        now_dt = dt.datetime.now()
        self.journal.open_access = False
        self.journal.type = JournalTypeFactory.create(code='S')
        self.journal.save()
        IssueFactory.create(
            journal=self.journal, year=now_dt.year - 3,
            date_published=dt.date(now_dt.year - 3, 3, 20))
        IssueFactory.create(
            journal=self.journal, year=now_dt.year - 1,
            date_published=dt.date(now_dt.year - 1, 3, 20))
        issue_3 = IssueFactory.create(
            journal=self.journal, year=now_dt.year - 5,
            date_published=dt.date(now_dt.year - 5, 3, 20))
        # Run & check
        self.assertEqual(list(self.journal.published_open_access_issues), [issue_3, ])

    def test_can_return_the_published_open_access_issues_year_coverage(self):
        # Setup
        now_dt = dt.datetime.now()
        self.journal.open_access = False
        self.journal.type = JournalTypeFactory.create(code='S')
        self.journal.save()
        IssueFactory.create(
            journal=self.journal, year=now_dt.year - 3,
            date_published=dt.date(now_dt.year - 3, 3, 20))
        IssueFactory.create(
            journal=self.journal, year=now_dt.year - 1,
            date_published=dt.date(now_dt.year - 1, 3, 20))
        issue_3 = IssueFactory.create(
            journal=self.journal, year=now_dt.year - 5,
            date_published=dt.date(now_dt.year - 5, 3, 20))
        issue_4 = IssueFactory.create(
            journal=self.journal, year=now_dt.year - 7,
            date_published=dt.date(now_dt.year - 5, 3, 20))
        # Run & check
        self.assertEqual(
            self.journal.published_open_access_issues_year_coverage,
            {'from': issue_4.year, 'to': issue_3.year})


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
        self.journal.open_access = False
        self.journal.type = JournalTypeFactory.create(code='S')
        self.journal.save()
        issue_1 = IssueFactory.create(
            journal=self.journal, year=now_dt.year - 3,
            date_published=dt.date(now_dt.year - 3, 3, 20))
        issue_2 = IssueFactory.create(
            journal=self.journal, year=now_dt.year - 1,
            date_published=dt.date(now_dt.year - 1, 3, 20))
        issue_3 = IssueFactory.create(
            journal=self.journal, year=now_dt.year - 5,
            date_published=dt.date(now_dt.year - 5, 3, 20))
        # Run & check
        self.assertTrue(issue_1.has_movable_limitation)
        self.assertTrue(issue_2.has_movable_limitation)
        self.assertFalse(issue_3.has_movable_limitation)

    def test_knows_if_it_has_a_movable_limitation_in_case_of_non_scientific_journals(self):
        # Setup
        now_dt = dt.datetime.now()
        self.journal.open_access = False
        self.journal.type = JournalTypeFactory.create(code='C')
        self.journal.save()
        issue_1 = IssueFactory.create(
            journal=self.journal, year=now_dt.year - 3,
            date_published=dt.date(now_dt.year - 3, 3, 20))
        issue_2 = IssueFactory.create(
            journal=self.journal, year=now_dt.year - 1,
            date_published=dt.date(now_dt.year - 1, 3, 20))
        issue_3 = IssueFactory.create(
            journal=self.journal, year=now_dt.year - 5,
            date_published=dt.date(now_dt.year - 5, 3, 20))
        # Run & check
        self.assertFalse(issue_1.has_movable_limitation)
        self.assertTrue(issue_2.has_movable_limitation)
        self.assertFalse(issue_3.has_movable_limitation)

    def test_knows_that_issues_with_open_access_has_no_movable_limitation(self):
        # Setup
        now_dt = dt.datetime.now()
        j2 = JournalFactory.create(collection=self.collection, open_access=False)
        self.journal.open_access = True
        self.journal.type = JournalTypeFactory.create(code='C')
        self.journal.save()
        issue_1 = IssueFactory.create(
            journal=self.journal, year=now_dt.year - 3,
            date_published=dt.date(now_dt.year - 3, 3, 20))
        issue_2 = IssueFactory.create(
            journal=self.journal, year=now_dt.year - 1,
            date_published=dt.date(now_dt.year - 1, 3, 20))
        issue_3 = IssueFactory.create(
            journal=j2, year=now_dt.year - 5,
            date_published=dt.date(now_dt.year - 5, 3, 20))
        # Run & check
        self.assertFalse(issue_1.has_movable_limitation)
        self.assertFalse(issue_2.has_movable_limitation)
        self.assertFalse(issue_3.has_movable_limitation)

    def test_knows_if_it_has_a_coverpage(self):
        # Setup
        self.journal.open_access = True
        self.journal.save()
        with open(settings.MEDIA_ROOT + '/coverpage.png', 'rb') as f:
            issue_1 = IssueFactory.create(journal=self.journal)
            issue_2 = IssueFactory.create(journal=self.journal)
            issue_1.fedora_object = unittest.mock.MagicMock()
            issue_1.fedora_object.coverpage = unittest.mock.MagicMock()
            issue_1.fedora_object.coverpage.content = io.BytesIO(f.read())
            issue_2.fedora_object = unittest.mock.MagicMock()
            issue_2.fedora_object.coverpage = unittest.mock.MagicMock()
            issue_2.fedora_object.coverpage.content = ''

        # Run & check
        self.assertTrue(issue_1.has_coverpage)
        self.assertFalse(issue_2.has_coverpage)

    def test_knows_that_an_issue_with_an_empty_coverpage_has_no_coverpage(self):
        # Setup
        self.journal.open_access = True
        self.journal.save()
        with open(settings.MEDIA_ROOT + '/coverpage_empty.png', 'rb') as f:
            issue = IssueFactory.create(journal=self.journal)
            issue.fedora_object = unittest.mock.MagicMock()
            issue.fedora_object.coverpage = unittest.mock.MagicMock()
            issue.fedora_object.coverpage.content = io.BytesIO(f.read())

        # Run & check
        self.assertFalse(issue.has_coverpage)

    def test_can_return_a_slug_that_can_be_used_in_urls(self):
        # Setup
        issue_1 = IssueFactory.create(
            journal=self.journal, year=2015, volume='4', number='1', localidentifier='i1')
        issue_2 = IssueFactory.create(
            journal=self.journal, year=2015, volume='4', number=None, localidentifier='i2')
        issue_3 = IssueFactory.create(
            journal=self.journal, year=2015, volume=None, number='2', localidentifier='i3')
        issue_4 = IssueFactory.create(
            journal=self.journal, year=2015, volume='2-3', number='39', localidentifier='i4')
        issue_5 = IssueFactory.create(
            journal=self.journal, year=2015, volume=None, number=None, localidentifier='i5')
        # Run & check
        self.assertEqual(issue_1.volume_slug, '2015-v4-n1')
        self.assertEqual(issue_2.volume_slug, '2015-v4')
        self.assertEqual(issue_3.volume_slug, '2015-n2')
        self.assertEqual(issue_4.volume_slug, '2015-v2-3-n39')
        self.assertEqual(issue_5.volume_slug, '2015')


class TestArticle(BaseEruditTestCase):

    def setUp(self):
        super(TestArticle, self).setUp()
        self.issue = IssueFactory.create(journal=self.journal)
        self.article = ArticleFactory.create(issue=self.issue)

    def test_knows_that_it_is_in_open_access_if_its_issue_is_in_open_access(self):
        # Setup
        j1 = JournalFactory.create(collection=self.collection, open_access=True)
        j2 = JournalFactory.create(collection=self.collection, open_access=False)
        issue_1 = IssueFactory.create(journal=j1)
        article_1 = ArticleFactory.create(issue=issue_1)
        issue_2 = IssueFactory.create(journal=j2)
        article_2 = ArticleFactory.create(issue=issue_2)
        # Run 1 check
        self.assertTrue(article_1.open_access)
        self.assertFalse(article_2.open_access)

    def test_knows_if_it_is_in_open_access_if_its_journal_is_in_open_access(self):
        # Setup
        self.journal.open_access = True
        self.journal.save()
        j2 = JournalFactory.create(collection=self.collection, open_access=False)
        issue_1 = IssueFactory.create(journal=self.journal)
        article_1 = ArticleFactory.create(issue=issue_1)
        issue_2 = IssueFactory.create(journal=j2)
        article_2 = ArticleFactory.create(issue=issue_2)
        # Run 1 check
        self.assertTrue(article_1.open_access)
        self.assertFalse(article_2.open_access)

    def test_knows_if_it_has_a_movable_limitation(self):
        # Setup
        now_dt = dt.datetime.now()
        self.journal.open_access = False
        self.journal.type = JournalTypeFactory.create(code='S')
        self.journal.save()
        issue_1 = IssueFactory.create(
            journal=self.journal, year=now_dt.year - 3,
            date_published=dt.date(now_dt.year - 3, 3, 20))
        issue_2 = IssueFactory.create(
            journal=self.journal, year=now_dt.year - 1,
            date_published=dt.date(now_dt.year - 1, 3, 20))
        issue_3 = IssueFactory.create(
            journal=self.journal, year=now_dt.year - 5,
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
