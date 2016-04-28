# -*- coding: utf-8 -*-

import datetime as dt

from django.test import RequestFactory

from erudit.factories import IssueFactory
from erudit.tests.base import BaseEruditTestCase

from ..feeds import LatestIssuesFeed


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
        self.assertIn(issue1.get_absolute_url(), feed.items[0]['link'])
        self.assertIn(issue2.get_absolute_url(), feed.items[1]['link'])
