import datetime
import pytest

from django.test import Client
from django.urls import reverse
from django.utils.feedgenerator import rfc2822_date
from django.utils.timezone import make_aware

from erudit.test.factories import ArticleFactory, IssueFactory, JournalFactory

pytestmark = pytest.mark.django_db


class TestLatestIssuesFeed:

    def _get_pubdate(self, date_published):
        return rfc2822_date(make_aware(
            datetime.datetime.combine(date_published, datetime.datetime.min.time())
        ))

    def test_rss_feed(self):
        now = datetime.datetime.now()
        # Issue published today, should appear first in the RSS
        issue1 = IssueFactory(
            date_published=now.date(),
            localidentifier='isssue1',
            journal__code='journal1',
            journal__name='journal1',
        )
        # Issue published yesterday, should appear second in the RSS
        issue2 = IssueFactory(
            date_published=now.date() - datetime.timedelta(1),
            localidentifier='isssue2',
            journal__code='journal2',
            journal__name='journal2',
        )
        # Unpublished issue, should not appear in the RSS
        issue3 = IssueFactory(
            is_published=False,
            localidentifier='isssue3',
        )
        # Older than 90 days issue, should not appear in the RSS
        issue4 = IssueFactory(
            date_published=now.date() - datetime.timedelta(91),
            localidentifier='isssue4',
        )

        rss = Client().get(reverse('public:journal:latest_issues_rss')).content.decode()

        # Check the feed's title
        assert '<title>Syndication d\'Érudit</title>' in rss
        # Check the feed's website link
        assert '<link>http://example.com/fr/</link>' in rss
        # Check the feed's description
        assert '<description>{start_date} - {today}</description>'.format(
            start_date=datetime.datetime.strftime(now - datetime.timedelta(90), '%Y/%m/%d'),
            today=datetime.datetime.strftime(now, '%Y/%m/%d'),
        ) in rss
        # Check the feed's language
        assert '<language>fr</language>' in rss
        # Check the feed's image
        assert '<image><url>/static/img/logo-erudit.png</url><title>Érudit</title><link>https://erudit.org</link></image>' in rss

        # Check the feed's items order
        assert '<item><title>journal1, Numéro 110, supplément, hiver 2012</title><link>http://example.com/fr/revues/journal1/{year}-isssue1/</link><pubDate>{pubdate1}</pubDate><guid>http://example.com/fr/revues/journal1/{year}-isssue1/</guid></item><item><title>journal2, Numéro 110, supplément, hiver 2012</title><link>http://example.com/fr/revues/journal2/{year}-isssue2/</link><pubDate>{pubdate2}</pubDate><guid>http://example.com/fr/revues/journal2/{year}-isssue2/</guid></item>'.format(
            year=now.year,
            pubdate1=self._get_pubdate(issue1.date_published),
            pubdate2=self._get_pubdate(issue2.date_published),
        ) in rss

        # Check that unpublished and old issues are not included
        assert 'issue3' not in rss
        assert 'issue4' not in rss


class TestLatestJournalArticlesFeed:

    def test_rss_feed(self):
        journal = JournalFactory(
            code='journal',
        )
        old_issue = IssueFactory(
            journal=journal,
            year='2011',
            localidentifier='old_issue',
        )
        latest_issue = IssueFactory(
            journal=journal,
            year='2012',
            localidentifier='latest_issue',
        )
        old_article = ArticleFactory(
            issue=old_issue,
            localidentifier='old_article',
        )
        article1 = ArticleFactory(
            issue=latest_issue,
            localidentifier='article1',
        )
        article2 = ArticleFactory(
            issue=latest_issue,
            localidentifier='article2',
        )

        rss = Client().get(reverse('public:journal:journal_articles_rss', kwargs={
            'code': journal.code,
        })).content.decode()

        # Check the feed's title
        assert '<title>Syndication d\'Érudit</title>' in rss
        # Check the feed's website link
        assert '<link>http://example.com/fr/</link>' in rss
        # Check the feed's description
        assert '<description>{description}</description>'.format(
            description=latest_issue.volume_title,
        ) in rss
        # Check the feed's language
        assert '<language>fr</language>' in rss
        # Check the feed's image
        assert '<image><url>/static/img/logo-erudit.png</url><title>Érudit</title><link>https://erudit.org</link></image>' in rss

        # Check the feed's items order
        assert '<item><title>Robert Southey, Writing and Romanticism</title><link>http://example.com/fr/revues/journal/2012-latest_issue/article1/</link><description>Lynda Pratt</description><guid>http://example.com/fr/revues/journal/2012-latest_issue/article1/</guid></item><item><title>Robert Southey, Writing and Romanticism</title><link>http://example.com/fr/revues/journal/2012-latest_issue/article2/</link><description>Lynda Pratt</description><guid>http://example.com/fr/revues/journal/2012-latest_issue/article2/</guid></item>'

        # Check that old issues and articles are not included
        assert 'old_issue' not in rss
        assert 'old_article' not in rss
