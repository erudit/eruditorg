import os
import pickle
import datetime as dt
import pytest

import unittest.mock
from django.urls import reverse
from django.test import Client

from erudit.test.factories import (
    IssueFactory,
    ArticleFactory,
)
from erudit.test.factories import JournalFactory

FIXTURE_ROOT = os.path.join(os.path.dirname(__file__), 'fixtures')


@pytest.mark.django_db
class TestHomeView:
    def test_embeds_the_latest_issues_into_the_context(self):
        # Setup
        issue_1 = IssueFactory.create(
            date_published=dt.datetime.now() - dt.timedelta(days=1))
        issue_2 = IssueFactory.create(journal=issue_1.journal, date_published=dt.datetime.now())
        url = reverse('public:home')
        # Run
        response = Client().get(url)
        # Check
        assert response.status_code == 200
        assert list(response.context['latest_issues']) == [issue_2, issue_1, ]

    @unittest.mock.patch("apps.public.views.rss_parse")
    def test_embeds_the_latest_news_into_the_context(self, mock_content):
        # Setup
        with open(os.path.join(FIXTURE_ROOT, 'news_rss_feed.pickle'), 'rb') as rss:
            mock_content.return_value = pickle.load(rss)
        url = reverse('public:home')
        # Run
        response = Client().get(url)
        # Check
        assert response.status_code == 200
        assert len(response.context['latest_news'])

    @unittest.mock.patch("apps.public.views.rss_parse", return_value={'status': 404})
    def test_can_display_home_page_when_news_are_unavailable(self, mock_content):

        # Setup
        url = reverse('public:home')
        # Run

        response = Client().get(url)
        # Check
        assert response.status_code == 200
        assert len(response.context['latest_news']) == 0

    def test_embeds_the_upcoming_year_new_journals_into_the_context(self):
        # Setup
        old_journal = JournalFactory()
        current_year_new_journal = JournalFactory(is_new=True)
        upcoming_year_new_journal = JournalFactory(is_new=True, year_of_addition='2020')
        url = reverse('public:home')
        # Run
        response = Client().get(url)
        # Check
        assert response.status_code == 200
        assert old_journal not in response.context['new_journals']
        assert current_year_new_journal not in response.context['new_journals']
        assert upcoming_year_new_journal in response.context['new_journals']

    def test_sitemaps(self):
        journal = JournalFactory()
        issues = IssueFactory.create_batch(100, journal=journal)
        for issue in issues:
            ArticleFactory.create_batch(11, issue=issue,
                                        solr_attrs={'DateAjoutIndex': '2018-09-21T20:16:50.149Z'})
        url = reverse('sitemaps', kwargs={'section': 'article'})
        response = Client().get(url)
        assert response.status_code == 200
        url = reverse('sitemap')
        response = Client().get(url)
        assert response.status_code == 200
