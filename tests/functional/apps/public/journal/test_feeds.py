# -*- coding: utf-8 -*-

import datetime as dt
import unittest.mock

from django.core.urlresolvers import reverse
from django.test import RequestFactory
from django.test.utils import override_settings

from erudit.test import BaseEruditTestCase
from erudit.test.factories import ArticleFactory
from erudit.test.factories import IssueFactory
from erudit.fedora.modelmixins import FedoraMixin

from apps.public.journal.feeds import LatestIssuesFeed
from apps.public.journal.feeds import LatestJournalArticlesFeed


def get_mocked_erudit_object():
    m = unittest.mock.MagicMock()
    m.ordseq = 1
    return m


@override_settings(DEBUG=True)
class TestLatestIssuesFeed(BaseEruditTestCase):
    def setUp(self):
        super(TestLatestIssuesFeed, self).setUp()
        self.factory = RequestFactory()

    def test_can_return_all_the_issues_published_since_a_specific_date(self):
        # Setup
        issue1 = IssueFactory.create(journal=self.journal, date_published=dt.datetime.now())
        issue2 = IssueFactory.create(
            journal=self.journal, date_published=dt.datetime.now() - dt.timedelta(days=20))
        IssueFactory.create(
            journal=self.journal, date_published=dt.datetime.now() - dt.timedelta(days=110))
        request = self.factory.get('/')
        # Run
        feed = LatestIssuesFeed().get_feed(None, request)
        # Check
        self.assertEqual(len(feed.items), 2)
        self.assertIn(
            reverse('public:journal:issue_detail',
                    args=[issue1.journal.code, issue1.volume_slug, issue1.localidentifier]),
            feed.items[0]['link'])
        self.assertIn(
            reverse('public:journal:issue_detail',
                    args=[issue2.journal.code, issue2.volume_slug, issue2.localidentifier]),
            feed.items[1]['link'])


class TestLatestJournalArticlesFeed(BaseEruditTestCase):
    def setUp(self):
        super(TestLatestJournalArticlesFeed, self).setUp()
        self.factory = RequestFactory()

    @unittest.mock.patch.object(FedoraMixin, 'get_erudit_object')
    def test_can_return_all_the_articles_associated_with_the_last_issue_of_a_journal(self, mock_erudit_object):  # noqa
        # Setup
        mock_erudit_object.return_value = get_mocked_erudit_object()
        issue1 = IssueFactory.create(
            journal=self.journal, year=2010, date_published=dt.datetime.now())
        article1 = ArticleFactory.create(issue=issue1)
        article2 = ArticleFactory.create(issue=issue1)
        issue2 = IssueFactory.create(
            journal=self.journal, year=2010,
            date_published=dt.datetime.now() - dt.timedelta(days=2))
        ArticleFactory.create(issue=issue2)
        request = self.factory.get('/')
        # Run
        f = LatestJournalArticlesFeed()
        f.get_object(request, self.journal.code)
        feed = f.get_feed(None, request)
        # Check
        self.assertEqual(len(feed.items), 2)
        self.assertIn(
            reverse('public:journal:article_detail',
                    args=[
                        article1.issue.journal.code,
                        article1.issue.volume_slug,
                        article1.issue.localidentifier,
                        article1.localidentifier
                    ]), feed.items[0]['link'])
        self.assertIn(
            reverse('public:journal:article_detail',
                    args=[
                        article2.issue.journal.code,
                        article2.issue.volume_slug,
                        article2.issue.localidentifier,
                        article2.localidentifier
                    ]), feed.items[1]['link'])
