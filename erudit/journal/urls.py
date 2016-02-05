# -*- coding: utf-8 -*-

from django.conf.urls import include
from django.conf.urls import url

from . import urls_compat
from . import views


urlpatterns = [
    url(r'^journal/(?P<code>[\w-]+)/$', views.JournalDetailView.as_view(), name='journal-detail'),

    url(r'^article/(?P<journalid>[\w-]+)\.(?P<issueid>[\w-]+)\.(?P<articleid>[.\w-]+)/$',
        views.ArticlePdfView.as_view(), name='article-pdf'),

    url(r'^article/(?P<journalid>[\w-]+)\.(?P<issueid>[\w-]+)\.(?P<articleid>[.\w-]+)\.pdf$',
        views.ArticleRawPdfView.as_view(), name='article-raw-pdf'),
    url(r'^article/(?P<journalid>[\w-]+)\.(?P<issueid>[\w-]+)\.(?P<articleid>[.\w-]+)/raw/$',
        views.ArticleRawPdfView.as_view(), name='article-raw-pdf'),

    # Compatibility URLs
    url('^', include(urls_compat.urlpatterns)),
]
