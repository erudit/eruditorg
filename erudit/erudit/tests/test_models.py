# -*- coding: utf-8 -*-

import datetime as dt

from eruditarticle.objects import EruditJournal
from eruditarticle.objects import EruditPublication

from erudit.fedora.objects import JournalDigitalObject
from erudit.fedora.objects import PublicationDigitalObject
from erudit.factories import IssueFactory, ArticleFactory

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
        IssueFactory.create(journal=self.journal, date_published=None)
        # Run & check
        self.assertEqual(list(self.journal.published_issues), [issue_1, issue_2, ])

    def test_can_return_its_first_issue(self):
        # Setup
        issue_1 = IssueFactory.create(
            journal=self.journal, date_published=dt.datetime.now() - dt.timedelta(days=1))
        IssueFactory.create(journal=self.journal, date_published=dt.datetime.now())
        IssueFactory.create(journal=self.journal, date_published=None)
        # Run & check
        self.assertEqual(self.journal.first_issue, issue_1)

    def test_can_return_its_last_issue(self):
        # Setup
        IssueFactory.create(
            journal=self.journal, date_published=dt.datetime.now() - dt.timedelta(days=1))
        issue_2 = IssueFactory.create(journal=self.journal, date_published=dt.datetime.now())
        IssueFactory.create(journal=self.journal, date_published=None)
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
        IssueFactory.create(journal=self.journal, date_published=None, open_access=True)
        # Run & check
        self.assertEqual(self.journal.last_oa_issue, issue_2)


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

    def test_cannot_have_a_full_identifier_without_localidentifier(self):
        # Setup
        self.issue.localidentifier = None
        self.issue.save()
        # Run & check
        self.assertIsNone(self.issue.get_full_identifier())

    def test_issue_do_not_have_a_full_identifier_if_the_journal_has_no_localidentifier(self):
        # Setup
        self.journal.localidentifier = None
        self.journal.save()
        self.issue.localidentifier = 'dummy1234'
        self.issue.save()
        # Run & check
        self.assertIsNone(self.issue.get_full_identifier())

    def test_can_return_an_appropriate_fedora_pid(self):
        # Setup
        self.journal.localidentifier = 'dummy139'
        self.journal.save()
        self.issue.localidentifier = 'dummy1234'
        self.issue.save()
        # Run & check
        self.assertEqual(self.issue.pid, 'erudit:erudit.dummy139.dummy1234')


class TestArticle(BaseEruditTestCase):

    def setUp(self):
        super(TestArticle, self).setUp()
        self.issue = IssueFactory.create(journal=self.journal)
        self.article = ArticleFactory.create(issue=self.issue)

    def test_article_do_not_have_a_full_identifier_if_the_issue_has_no_localidentifier(self):
        # Setup
        self.issue.localidentifier = None
        self.issue.save()
        self.article.localidentifier = 'dummy1234'
        self.article.save()
        # Run & check
        self.assertIsNone(self.article.get_full_identifier())
