# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.views.generic import RedirectView

from base.views import DummyView

from . import views_compat


unsupported_patterns = [
    r'^revue/(?P<code>[\w-]+)/thematique.html?$',
    r'^revue/(?P<code>[\w-]+)/apropos.html?$',
    r'^revue/redirection/(?P<code>[\w-]+)/',

    r'^culture/(?P<code>[\w-]+)/thematique.html?$',

    r'^feuilletage/index.html?$',
    r'^feuilletage_(?P<code1>[\w-]+)\.(?P<code2>[\w-]+)@(?P<id>[0-9]+)$',
    (r'^feuilletage_(?P<code1>[\w-]+)\.(?P<code2>[\w-]+)@(?P<id>[0-9]+)'
     '(?:\&(?P<key>[\w-]+)=(?P<val>[\w-]+))*$'),
]

urlpatterns = [
    # Journal
    url(r'^revue/(?P<code>[\w-]+)/$',
        RedirectView.as_view(pattern_name='public:journal:journal-detail', permanent=True)),
    url(r'^revue/(?P<code>[\w-]+)/index\.html?$',
        RedirectView.as_view(pattern_name='public:journal:journal-detail', permanent=True)),
    url(r'^revue/(?P<code>[\w-]+)/auteurs\.html?$',
        RedirectView.as_view(pattern_name='public:journal:journal-authors-list', permanent=True)),
    url(r'^culture/(?P<code>[\w-]+)/$',
        RedirectView.as_view(pattern_name='public:journal:journal-detail', permanent=True)),
    url(r'^culture/(?P<code>[\w-]+)/index.html?$',
        RedirectView.as_view(pattern_name='public:journal:journal-detail', permanent=True)),
    url(r'^culture/(?P<code>[\w-]+)/auteurs\.html?$',
        RedirectView.as_view(pattern_name='public:journal:journal-authors-list', permanent=True)),
    url(r'^culture/(?P<journal_code>[\w-]+)/rss\.xml$',
        RedirectView.as_view(pattern_name='public:journal:journal-issues-rss', permanent=True)),

    # Issue
    url(r'^revue/(?P<journal_code>[\w-]+)/(?P<year>\d{4})/v(?P<v>[\w-]+)/n(?P<n>[\w-]+)/$',
        views_compat.IssueDetailRedirectView.as_view()),
    url(r'^revue/(?P<journal_code>[\w-]+)/(?P<year>\d{4})/v(?P<v>[\w-]+)/n(?P<n>[\w-]+)/index\.html?$',  # noqa
        views_compat.IssueDetailRedirectView.as_view()),
    url(r'^revue/(?P<journal_code>[\w-]+)/(?P<year>\d{4})/v(?P<v>[\w-]+)/n/$',
        views_compat.IssueDetailRedirectView.as_view()),
    url(r'^revue/(?P<journal_code>[\w-]+)/(?P<year>\d{4})/v(?P<v>[\w-]+)/n/index\.html?$',
        views_compat.IssueDetailRedirectView.as_view()),
    url(r'^revue/(?P<journal_code>[\w-]+)/(?P<year>\d{4})/v(?P<v>\d+)/(?P<localidentifier>[\w-]+)/?$',  # noqa
        views_compat.IssueDetailRedirectView.as_view()),
    url(r'^revue/(?P<journal_code>[\w-]+)/(?P<year>\d{4})/v(?P<v>\d+)/(?P<localidentifier>[\w-]+)/index\.html?$',  # noqa
        views_compat.IssueDetailRedirectView.as_view()),
    url(r'^culture/(?P<journal_code>[\w-]+)/(?P<year>\d{4})/v(?P<v>\d+)/(?P<localidentifier>[\w-]+)/?$',  # noqa
        views_compat.IssueDetailRedirectView.as_view()),
    url(r'^culture/(?P<journal_code>[\w-]+)/(?P<year>\d{4})/v(?P<v>\d+)/(?P<localidentifier>[\w-]+)/index\.html?$',  # noqa
        views_compat.IssueDetailRedirectView.as_view()),
    url(r'^culture/(?P<journal_code>[\w-]+)/(?P<localidentifier>[\w-]+)/?$',
        views_compat.IssueDetailRedirectView.as_view()),
    url(r'^culture/(?P<journal_code>[\w-]+)/(?P<localidentifier>[\w-]+)/index\.html?$',
        views_compat.IssueDetailRedirectView.as_view()),

    # Article
    url(r'^revue/(?P<journal_code>[\w-]+)/(?P<year>\d{4})/(?P<v>[\w-]+)/(?P<issue_localid>[\w-]+)/(?P<localid>[\w-]+)\.html?$',  # noqa
        views_compat.ArticleDetailRedirectView.as_view()),
    url(r'^iderudit/(?P<localid>[\w-]+)$', views_compat.ArticleDetailRedirectView.as_view()),
    url(r'^culture/(?P<journal_code>[\w-]+)/(?P<year>\d{4})/(?P<v>[\w-]+)/(?P<issue_localid>[\w-]+)/(?P<localid>[\w-]+)\.html?$',  # noqa
        views_compat.ArticleDetailRedirectView.as_view()),
    url(r'^culture/(?P<journal_code>[\w-]+)/(?P<issue_localid>[\w-]+)/(?P<localid>[\w-]+)\.html?$',
        views_compat.ArticleDetailRedirectView.as_view()),
]

urlpatterns += [url(pattern_re, DummyView.as_view()) for pattern_re in unsupported_patterns]
