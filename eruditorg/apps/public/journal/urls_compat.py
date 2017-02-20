# -*- coding: utf-8 -*-

from django.conf.urls import url

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
        views_compat.JournalDetailCheckRedirectView.as_view(
            pattern_name='public:journal:journal_detail', permanent=True),
        name="legacy_journal_detail"),
    url(r'^revue/(?P<code>[\w-]+)/index\.html?$',
        views_compat.JournalDetailCheckRedirectView.as_view(
            pattern_name='public:journal:journal_detail', permanent=True),
        name="legacy_journal_detail_index"),
    url(r'^revue/(?P<code>[\w-]+)/auteurs\.html?$',
        views_compat.JournalDetailCheckRedirectView.as_view(
            pattern_name='public:journal:journal_authors_list', permanent=True),
        name="legacy_journal_authors"),
    url(r'^culture/(?P<code>[\w-]+)/$',
        views_compat.JournalDetailCheckRedirectView.as_view(
            pattern_name='public:journal:journal_detail', permanent=True),
        name="legacy_journal_detail_culture"),
    url(r'^culture/(?P<code>[\w-]+)/index.html?$',
        views_compat.JournalDetailCheckRedirectView.as_view(
            pattern_name='public:journal:journal_detail', permanent=True),
        name="legacy_journal_detail_culture_index"),
    url(r'^culture/(?P<code>[\w-]+)/auteurs\.html?$',
        views_compat.JournalDetailCheckRedirectView.as_view(
            pattern_name='public:journal:journal_authors_list', permanent=True),
        name="legacy_journal_authors_culture"),
    url(r'^culture/(?P<code>[\w-]+)/rss\.xml$',
        views_compat.JournalDetailCheckRedirectView.as_view(
            pattern_name='public:journal:journal_articles_rss', permanent=True),
        name="legacy_journal_rss"),

    # Issue
    url(r'^revue/(?P<journal_code>[\w-]+)/(?P<year>\d{4})/v(?P<v>[\w-]*)/n(?P<n>[\w-]+)/$',
        views_compat.IssueDetailRedirectView.as_view(),
        name="legacy_issue_detail"),
    url(r'^revue/(?P<journal_code>[\w-]+)/(?P<year>\d{4})/v(?P<v>[\w-]*)/n(?P<n>[\w-]+)/index\.html?$',  # noqa
        views_compat.IssueDetailRedirectView.as_view(),
        name="legacy_issue_detail_index"),
    url(r'^revue/(?P<journal_code>[\w-]+)/(?P<year>\d{4})/v(?P<v>[\w-]*)/n/$',
        views_compat.IssueDetailRedirectView.as_view(),
        name="legacy_issue_detail_no_number"),
    url(r'^revue/(?P<journal_code>[\w-]+)/(?P<year>\d{4})/v(?P<v>[\w-]*)/n/index\.html?$',
        views_compat.IssueDetailRedirectView.as_view(),
        name="legacy_issue_detail_index_no_number"),
    url(r'^culture/(?P<journal_code>[\w-]+)/(?P<year>\d{4})/v(?P<v>[\w-]*)/(?P<localidentifier>[\w-]+)/?$',  # noqa
        views_compat.IssueDetailRedirectView.as_view(),
        name="legacy_issue_detail_culture_year_volume"),
    url(r'^culture/(?P<journal_code>[\w-]+)/(?P<year>\d{4})/v(?P<v>[\w-]*)/(?P<localidentifier>[\w-]+)/index\.html?$',  # noqa
        views_compat.IssueDetailRedirectView.as_view(),
        name="legacy_issue_detail_culture_year_volume_index"),
    url(r'^culture/(?P<journal_code>[\w-]+)/(?P<localidentifier>[\w-]+)/?$',
        views_compat.IssueDetailRedirectView.as_view(),
        name="legacy_issue_detail_culture"),
    url(r'^culture/(?P<journal_code>[\w-]+)/(?P<localidentifier>[\w-]+)/index\.html?$',
        views_compat.IssueDetailRedirectView.as_view(),
        name="legacy_issue_detail_culture_index"),

    # Article
    url(r'^revue/(?P<journal_code>[\w-]+)/(?P<year>\d{4})/v(?P<v>[\w-]*)/(?P<issue_localid>[\w-]+)/(?P<localid>[\w-]+)\.(?P<format_identifier>[\w-]+)?$',  # noqa
        views_compat.ArticleDetailRedirectView.as_view(),
        name="legacy_article_detail"),
    url(r'^iderudit/(?P<localid>[\w-]+)$',
        views_compat.ArticleDetailRedirectView.as_view(),
        name="legacy_article_id",
    ),
    url(r'^culture/(?P<journal_code>[\w-]+)/(?P<year>\d{4})/v(?P<v>[\w-]*)/(?P<issue_localid>[\w-]+)/(?P<localid>[\w-]+)\.(?P<format_identifier>[\w-]+)?$',  # noqa
        views_compat.ArticleDetailRedirectView.as_view(),
        name="legacy_article_detail_culture"
    ),
    url(r'^culture/(?P<journal_code>[\w-]+)/(?P<issue_localid>[\w-]+)/(?P<localid>[\w-]+)\.(?P<format_identifier>[\w-]+)?$',  # noqa
        views_compat.ArticleDetailRedirectView.as_view(),
        name="legacy_article_detail_culture_localidentifier"
    )
]

urlpatterns += [url(pattern_re, DummyView.as_view()) for pattern_re in unsupported_patterns]
