# -*- coding: utf-8 -*-

import datetime as dt

from django.core.urlresolvers import reverse
from django.test.utils import override_settings

from erudit.test.factories import IssueFactory
from erudit.test.factories import JournalFactory
from erudit.test import BaseEruditTestCase


@override_settings(DEBUG=True)
class TestHomeView(BaseEruditTestCase):
    def test_embeds_the_latest_issues_into_the_context(self):
        # Setup
        issue_1 = IssueFactory.create(
            journal=self.journal, date_published=dt.datetime.now() - dt.timedelta(days=1))
        issue_2 = IssueFactory.create(journal=self.journal, date_published=dt.datetime.now())
        url = reverse('public:home')
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['latest_issues']), [issue_2, issue_1, ])

    def test_embeds_the_latest_news_into_the_context(self):
        # Setup
        url = reverse('public:home')
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['latest_news']))

    def test_embeds_the_upcoming_journals_into_the_context(self):
        # Setup
        JournalFactory.create(collection=self.collection, upcoming=False)
        url = reverse('public:home')
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 200)
