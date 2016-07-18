# -*- coding: utf-8 -*-

from django.conf.urls import include
from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from . import feeds
from . import urls_compat
from . import views


urlpatterns = [
    url(_(r'^revues/$'), views.JournalListView.as_view(), name='journal_list'),
    url(_(r'^rss\.xml$'), feeds.LatestIssuesFeed(), name='latest_issues_rss'),

    # Journal URLs
    url(_(r'^revues/(?P<code>[\w-]+)/'), include([
        url(r'^$', views.JournalDetailView.as_view(), name='journal_detail'),
        url(_(r'^logo.jpg$'), views.JournalRawLogoView.as_view(), name='journal_logo'),
        url(_(r'^auteurs/$'), views.JournalAuthorsListView.as_view(), name='journal_authors_list'),
        url(r'^rss\.xml$', feeds.LatestJournalArticlesFeed(), name='journal_articles_rss'),
    ])),

    # Issue URLs
    url(_(r'^revues/(?P<journal_code>[\w-]+)/(?P<issue_slug>[\w-]*)-(?P<localidentifier>[\w-]+)/'), include([  # noqa
        url(r'^$', views.IssueDetailView.as_view(), name='issue_detail'),
        url(_(r'^logo.jpg$'), views.IssueRawCoverpageView.as_view(), name='issue_coverpage'),
    ])),

    # Article URLs
    url(_(r'^revues/(?P<journal_code>[\w-]+)/(?P<issue_slug>[\w-]*)-(?P<issue_localid>[\w-]+)/(?P<localid>[\w-]+)/'), include([  # noqa
        url(r'^$', views.ArticleDetailView.as_view(), name='article_detail'),
        url(_(r'^resume/$'), views.ArticleSummaryView.as_view(), name='article_summary'),
        url(_(r'^media/(?P<media_localid>[.\w-]+)$'), views.ArticleMediaView.as_view(), name='article_media'),  # noqa
        url(_(r'^citation\.enw$'), views.ArticleEnwCitationView.as_view(), name='article_citation_enw'),  # noqa
        url(_(r'^citation\.ris$'), views.ArticleRisCitationView.as_view(), name='article_citation_ris'),  # noqa
        url(_(r'^citation\.bib$'), views.ArticleBibCitationView.as_view(), name='article_citation_bib'),  # noqa
        url(_(r'^contenu\.pdf$'), views.ArticleRawPdfView.as_view(), name='article_raw_pdf'),
    ])),

    # Compatibility URLs
    url('^', include(urls_compat.urlpatterns)),

    # Journal catchall
    url(r'^(?P<code>[\w-]+)/$', views.JournalDetailView.as_view(), name='journal_detail'),
]
