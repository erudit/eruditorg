import datetime as dt
import pytest

from django.urls import reverse
from django.test import RequestFactory

from erudit.test.factories import ArticleFactory
from erudit.test.factories import IssueFactory
from erudit.test.factories import JournalFactory

from apps.public.journal.feeds import LatestIssuesFeed
from apps.public.journal.feeds import LatestJournalArticlesFeed


pytestmark = pytest.mark.django_db

class TestLatestIssuesFeed:
    def test_can_return_all_the_issues_published_since_a_specific_date(self):
        issue1 = IssueFactory.create(date_published=dt.datetime.now())
        issue2 = IssueFactory.create(
            journal=issue1.journal, date_published=dt.datetime.now() - dt.timedelta(days=20))
        IssueFactory.create(
            journal=issue1.journal, date_published=dt.datetime.now() - dt.timedelta(days=110))
        # Don't show unpublished issues
        IssueFactory.create(
            journal=issue1.journal, date_published=dt.datetime.now(), is_published=False)
        request = RequestFactory().get('/')
        feed = LatestIssuesFeed().get_feed(None, request)
        assert len(feed.items) == 2
        URL = reverse('public:journal:issue_detail',
            args=[issue1.journal.code, issue1.volume_slug, issue1.localidentifier])
        assert URL in feed.items[0]['link']
        URL = reverse('public:journal:issue_detail',
            args=[issue2.journal.code, issue2.volume_slug, issue2.localidentifier])
        assert URL in feed.items[1]['link']


class TestLatestJournalArticlesFeed:
    def test_can_return_all_the_articles_associated_with_the_last_issue_of_a_journal(self):
        journal = JournalFactory()
        issue1 = IssueFactory.create(journal=journal, is_published=True)
        issue2 = IssueFactory.create(journal=journal, is_published=True)
        ArticleFactory.create(issue=issue1)
        article1 = ArticleFactory.create(issue=issue2)
        article2 = ArticleFactory.create(issue=issue2)
        request = RequestFactory().get('/')
        f = LatestJournalArticlesFeed()
        f.get_object(request, journal.code)
        feed = f.get_feed(None, request)
        assert len(feed.items) == 2
        URL = reverse(
            'public:journal:article_detail',
            args=[
                article1.issue.journal.code,
                article1.issue.volume_slug,
                article1.issue.localidentifier,
                article1.localidentifier
            ])
        assert URL in feed.items[0]['link']
        URL = reverse(
            'public:journal:article_detail',
            args=[
                article2.issue.journal.code,
                article2.issue.volume_slug,
                article2.issue.localidentifier,
                article2.localidentifier
            ])
        assert URL in feed.items[1]['link']
