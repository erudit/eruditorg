# -*- coding: utf-8 -*-

from django.conf.urls import include
from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from . import feeds
from . import urls_compat
from . import views


urlpatterns = [
    url(_(r'^rss\.xml$'), feeds.LatestIssuesFeed(), name='latest_issues_rss'),

    url(_(r'^revues/$'),
        views.JournalListView.as_view(), name='journal_list'),

    url(_(r'^revue/(?P<code>[\w-]+)/$'),
        views.JournalDetailView.as_view(), name='journal_detail'),
    url(_(r'^revue/(?P<code>[\w-]+)/logo.jpg$'),
        views.JournalRawLogoView.as_view(), name='journal_logo'),
    url(_(r'^revue/(?P<code>[\w-]+)/auteurs/$'),
        views.JournalAuthorsListView.as_view(), name='journal_authors_list'),

    url(_(r'^revue/(?P<journal_code>[\w-]+)/rss\.xml$'),
        feeds.LatestJournalArticlesFeed(), name='journal_articles_rss'),

    url(_(r'^revue/(?P<journal_code>[\w-]+)/numero/(?P<pk>\d+)/$'),
        views.IssueDetailView.as_view(), name='issue_detail'),
    url(_(r'^revue/(?P<journal_code>[\w-]+)/numero/(?P<localidentifier>[\w-]+)/$'),
        views.IssueDetailView.as_view(), name='issue_detail'),

    url(_(r'^numero/(?P<pk>[\d-]+)/logo.jpg$'),
        views.IssueRawCoverpageView.as_view(), name='issue_coverpage'),

    url(_(r'^revue/(?P<journal_code>[\w-]+)/numero/(?P<issue_localid>[\w-]+)/'
          'article/(?P<pk>\d+)/$'),
        views.ArticleDetailView.as_view(), name='article_detail'),
    url(_(r'^revue/(?P<journal_code>[\w-]+)/numero/(?P<issue_localid>[\w-]+)/'
          'article/(?P<localid>[\w-]+)/$'),
        views.ArticleDetailView.as_view(), name='article_detail'),

    url(_(r'^revue/(?P<journal_code>[\w-]+)/numero/(?P<issue_localid>[\w-]+)/'
          'article/(?P<pk>\d+)/resume/$'),
        views.ArticleSummaryView.as_view(), name='article_summary'),
    url(_(r'^revue/(?P<journal_code>[\w-]+)/numero/(?P<issue_localid>[\w-]+)/'
          'article/(?P<localid>[\w-]+)/resume/$'),
        views.ArticleSummaryView.as_view(), name='article_summary'),

    url(_(r'^revue/(?P<journal_code>[\w-]+)/numero/(?P<issue_localid>[\w-]+)/'
          'article/(?P<articlepk>\d+)/media/(?P<localidentifier>[.\w-]+)$'),
        views.ArticleMediaView.as_view(), name='article_media'),
    url(_(r'^revue/(?P<journal_code>[\w-]+)/numero/(?P<issue_localid>[\w-]+)/'
          'article/(?P<articleid>[\w-]+)/media/(?P<localidentifier>[.\w-]+)$'),
        views.ArticleMediaView.as_view(), name='article_media'),

    url(_(r'^revue/(?P<journal_code>[\w-]+)/numero/(?P<issue_localid>[\w-]+)/'
          'article/(?P<pk>\d+)\.enw$'),
        views.ArticleEnwCitationView.as_view(), name='article_citation_enw'),
    url(_(r'^revue/(?P<journal_code>[\w-]+)/numero/(?P<issue_localid>[\w-]+)/'
          'article/(?P<localid>[\w-]+)\.enw$'),
        views.ArticleEnwCitationView.as_view(), name='article_citation_enw'),
    url(_(r'^revue/(?P<journal_code>[\w-]+)/numero/(?P<issue_localid>[\w-]+)/'
          'article/(?P<pk>\d+)\.ris$'),
        views.ArticleRisCitationView.as_view(), name='article_citation_ris'),
    url(_(r'^revue/(?P<journal_code>[\w-]+)/numero/(?P<issue_localid>[\w-]+)/'
          'article/(?P<localid>[\w-]+)\.ris$'),
        views.ArticleRisCitationView.as_view(), name='article_citation_ris'),
    url(_(r'^revue/(?P<journal_code>[\w-]+)/numero/(?P<issue_localid>[\w-]+)/'
          'article/(?P<pk>\d+)\.bib$'),
        views.ArticleBibCitationView.as_view(), name='article_citation_bib'),
    url(_(r'^revue/(?P<journal_code>[\w-]+)/numero/(?P<issue_localid>[\w-]+)/'
          'article/(?P<localid>[\w-]+)\.bib$'),
        views.ArticleBibCitationView.as_view(), name='article_citation_bib'),

    url(_(r'^article/(?P<journalid>[\w-]+)\.(?P<issueid>[\w-]+)\.(?P<articleid>[.\w-]+)/$'),
        views.ArticlePdfView.as_view(), name='article_pdf'),

    url(_(r'^article/(?P<articleid>[.\w-]+)\.pdf$'),
        views.ArticleRawPdfView.as_view(), name='article_raw_pdf'),
    url(_(r'^article/(?P<journalid>[\w-]+)\.(?P<issueid>[\w-]+)\.(?P<articleid>[.\w-]+)\.pdf$'),
        views.ArticleRawPdfView.as_view(), name='article_raw_pdf'),
    url(_(r'^article/(?P<journalid>[\w-]+)\.(?P<issueid>[\w-]+)\.(?P<articleid>[.\w-]+)/raw/$'),
        views.ArticleRawPdfView.as_view(), name='article_raw_pdf'),

    # Compatibility URLs
    url('^', include(urls_compat.urlpatterns)),

    # Journal catchall
    url(r'^(?P<code>[\w-]+)/$', views.JournalDetailView.as_view(), name='journal_detail'),
]
