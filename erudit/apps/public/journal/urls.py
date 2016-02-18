# -*- coding: utf-8 -*-

from django.conf.urls import include
from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from . import urls_compat
from . import views


urlpatterns = [
    url(_(r'^revues/$'),
        views.JournalListView.as_view(), name='journal-list'),

    url(_(r'^revue/(?P<code>[\w-]+)/$'),
        views.JournalDetailView.as_view(), name='journal-detail'),
    url(_(r'^revue/(?P<code>[\w-]+)/logo.jpg$'),
        views.JournalRawLogoView.as_view(), name='journal-logo'),

    url(_(r'^revue/(?P<journal_code>[\w-]+)/numero/(?P<pk>\d+)/$'),
        views.IssueDetailView.as_view(), name='issue-detail'),
    url(_(r'^revue/(?P<journal_code>[\w-]+)/numero/(?P<localidentifier>[\w-]+)/$'),
        views.IssueDetailView.as_view(), name='issue-detail'),

    url(_(r'^numero/(?P<pk>[\d-]+)/logo.jpg$'),
        views.IssueRawCoverpageView.as_view(), name='issue-coverpage'),

    url(_(r'^revue/(?P<journal_code>[\w-]+)/numero/(?P<issue_localid>[\w-]+)/'
          'article/(?P<pk>\d+)/$'),
        views.ArticleDetailView.as_view(), name='article-detail'),
    url(_(r'^revue/(?P<journal_code>[\w-]+)/numero/(?P<issue_localid>[\w-]+)/'
          'article/(?P<localid>[\w-]+)/$'),
        views.ArticleDetailView.as_view(), name='article-detail'),

    url(_(r'^article/(?P<journalid>[\w-]+)\.(?P<issueid>[\w-]+)\.(?P<articleid>[.\w-]+)/$'),
        views.ArticlePdfView.as_view(), name='article-pdf'),

    url(_(r'^article/(?P<journalid>[\w-]+)\.(?P<issueid>[\w-]+)\.(?P<articleid>[.\w-]+)\.pdf$'),
        views.ArticleRawPdfView.as_view(), name='article-raw-pdf'),
    url(_(r'^article/(?P<journalid>[\w-]+)\.(?P<issueid>[\w-]+)\.(?P<articleid>[.\w-]+)/raw/$'),
        views.ArticleRawPdfView.as_view(), name='article-raw-pdf'),

    # Compatibility URLs
    url('^', include(urls_compat.urlpatterns)),

    # Journal catchall
    url(r'^(?P<code>[\w-]+)/$', views.JournalDetailView.as_view(), name='journal-detail'),
]
