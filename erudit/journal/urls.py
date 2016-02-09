# -*- coding: utf-8 -*-

from django.conf.urls import include
from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from . import urls_compat
from . import views


urlpatterns = [
    url(_(r'^journal/information/$'),
        views.JournalInformationDispatchView.as_view(), name='journal-information'),
    url(_(r'^journal/information/liste/$'),
        views.JournalInformationListView.as_view(), name='journal-information-list'),
    url(_(r'^journal/information/(?P<code>[\w-]+)/edition/$'),
        views.JournalInformationUpdateView.as_view(), name='journal-information-update'),

    url(_(r'^journal/(?P<code>[\w-]+)/$'),
        views.JournalDetailView.as_view(), name='journal-detail'),

    url(_(r'^article/(?P<journalid>[\w-]+)\.(?P<issueid>[\w-]+)\.(?P<articleid>[.\w-]+)/$'),
        views.ArticlePdfView.as_view(), name='article-pdf'),

    url(_(r'^article/(?P<journalid>[\w-]+)\.(?P<issueid>[\w-]+)\.(?P<articleid>[.\w-]+)\.pdf$'),
        views.ArticleRawPdfView.as_view(), name='article-raw-pdf'),
    url(_(r'^article/(?P<journalid>[\w-]+)\.(?P<issueid>[\w-]+)\.(?P<articleid>[.\w-]+)/raw/$'),
        views.ArticleRawPdfView.as_view(), name='article-raw-pdf'),

    # Compatibility URLs
    url('^', include(urls_compat.urlpatterns)),
]
