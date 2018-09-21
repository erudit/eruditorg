# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.conf.urls import include

from .views import RedirectRetroUrls
from apps.public.journal import views_compat as journal_views_compat
from apps.public.book import views_compat as book_views_compat

# Thesis url patterns
# -----------------------------------------------------------------------------

thesis_url_patterns = [
    url(r'^$', RedirectRetroUrls.as_view(
        pattern_name='public:thesis:home',
        permanent=True)),
    url(r'^liste.html?$', RedirectRetroUrls.as_view(
        pattern_name='public:thesis:home',
        permanent=True
    )),
    url(r'^index.html?$', RedirectRetroUrls.as_view(
        pattern_name='public:thesis:home',
        permanent=True
    )),

]

# Public legacy patterns
# -----------------------------------------------------------------------------

public_url_patterns = [
    url(r'^client/login.jsp$',
        RedirectRetroUrls.as_view(pattern_name='public:auth:login', permanent=True)),
    url(r'^client/getNewPassword.jsp$',
        RedirectRetroUrls.as_view(pattern_name='public:auth:password_reset', permanent=True)),
    url(r'^client/updatePassword.jsp$',
        RedirectRetroUrls.as_view(pattern_name='public:auth:password_reset', permanent=True)),
]

# Search legacy patterns
# -----------------------------------------------------------------------------

search_url_patterns = [
    url(r'^index\.html?$',
        RedirectRetroUrls.as_view(pattern_name='public:search:advanced_search', permanent=True))
]

# Journal legacy patterns
# ------------------------------------------------------------------------------

journal_url_patterns = [
    # Journal
    url(r'^revue/(?P<code>[\w-]+)/?$',
        journal_views_compat.JournalDetailCheckRedirectView.as_view(
            pattern_name='public:journal:journal_detail', permanent=True),
        name="legacy_journal_detail"),
    url(r'^revue/(?P<code>[\w-]+)/index\.html?$',
        journal_views_compat.JournalDetailCheckRedirectView.as_view(
            pattern_name='public:journal:journal_detail', permanent=True),
        name="legacy_journal_detail_index"),
    url(r'^revue/(?P<code>[\w-]+)/auteurs\.html?$',
        journal_views_compat.JournalDetailCheckRedirectView.as_view(
            pattern_name='public:journal:journal_authors_list', permanent=True),
        name="legacy_journal_authors"),
    url(r'^culture/(?P<code>[\w-]+)/?$',
        journal_views_compat.JournalDetailCheckRedirectView.as_view(
            pattern_name='public:journal:journal_detail', permanent=True),
        name="legacy_journal_detail_culture"),
    url(r'^culture/(?P<code>[\w-]+)/index.html?$',
        journal_views_compat.JournalDetailCheckRedirectView.as_view(
            pattern_name='public:journal:journal_detail', permanent=True),
        name="legacy_journal_detail_culture_index"),
    url(r'^culture/(?P<code>[\w-]+)/auteurs\.html?$',
        journal_views_compat.JournalDetailCheckRedirectView.as_view(
            pattern_name='public:journal:journal_authors_list', permanent=True),
        name="legacy_journal_authors_culture"),
    url(r'^culture/(?P<code>[\w-]+)/rss\.xml$',
        journal_views_compat.JournalDetailCheckRedirectView.as_view(
            pattern_name='public:journal:journal_articles_rss', permanent=True),
        name="legacy_journal_rss"),

    # Issue
    url(r'^revue/(?P<journal_code>[\w-]+)/(?P<year>\d{4})/v(?P<v>[\w-]*)/n(?P<n>[\w-]+)/?$',  # noqa
        journal_views_compat.IssueDetailRedirectView.as_view(),
        name="legacy_issue_detail"),
    url(r'^revue/(?P<journal_code>[\w-]+)/(?P<year>\d{4})/v(?P<v>[\w-]*)/n(?P<n>[\w-]+)/index\.html?$',  # noqa
        journal_views_compat.IssueDetailRedirectView.as_view(),
        name="legacy_issue_detail_index"),
    url(r'^revue/(?P<journal_code>[\w-]+)/(?P<year>\d{4})/v(?P<v>[\w-]*)/n/?$',  # noqa
        journal_views_compat.IssueDetailRedirectView.as_view(),
        name="legacy_issue_detail_no_number"),
    url(r'^revue/(?P<journal_code>[\w-]+)/(?P<year>\d{4})/v(?P<v>[\w-]*)/n/index\.html?$',  # noqa
        journal_views_compat.IssueDetailRedirectView.as_view(),
        name="legacy_issue_detail_index_no_number"),
    url(r'^culture/(?P<journal_code>[\w-]+)/(?P<year>\d{4})/v(?P<v>[\w-]*)/(?P<localidentifier>[\w-]+)/?$',  # noqa
        journal_views_compat.IssueDetailRedirectView.as_view(),
        name="legacy_issue_detail_culture_year_volume"),
    url(r'^culture/(?P<journal_code>[\w-]+)/(?P<year>\d{4})/v(?P<v>[\w-]*)/(?P<localidentifier>[\w-]+)/[\w-]+\.html?$',  # noqa
        journal_views_compat.IssueDetailRedirectView.as_view(),
        name="legacy_issue_detail_culture_year_volume_index"),
    url(r'^culture/(?P<journal_code>[\w-]+)/(?P<localidentifier>[\w-]+)/?$',
        journal_views_compat.IssueDetailRedirectView.as_view(),
        name="legacy_issue_detail_culture"),
    url(r'^culture/(?P<journal_code>[\w-]+)/(?P<localidentifier>[\w-]+)/index\.html?$',  # noqa
        journal_views_compat.IssueDetailRedirectView.as_view(),
        name="legacy_issue_detail_culture_index"),

    # Article
    url(r'^revue/(?P<journal_code>[\w-]+)/(?P<year>\d{4})/v(?P<v>[\w-]*)/n(?P<issue_number>[\w-]+)/(?P<localid>[\w-]+)\.(?P<format_identifier>[\w-]+)?$',  # noqa
        journal_views_compat.ArticleDetailRedirectView.as_view(),
        name="legacy_article_detail",
    ),
    url(r'^revue/(?P<journal_code>[\w-]+)/(?P<year>\d{4})/v/n/(?P<localid>[\w-]+)\.(?P<format_identifier>[\w-]+)?$',  # noqa
        journal_views_compat.ArticleDetailRedirectView.as_view(),
        name="legacy_article_detail_no_volume_no_number",
    ),
    url(r'^revue/(?P<journal_code>[\w-]+)/(?P<year>\d{4})/v(?P<volume_number>\w+)/n/(?P<localid>[\w-]+)\.html$',  # noqa
        journal_views_compat.ArticleDetailRedirectView.as_view(),
        name="legacy_article_detail_volume"
    ),
    url(r'^iderudit/(?P<localid>[\w-]+)$',
        journal_views_compat.ArticleDetailRedirectView.as_view(),
        name="legacy_article_id",
    ),
    url(r'^culture/(?P<journal_code>[\w-]+)/(?P<year>\d{4})/v(?P<v>[\w-]*)/n(?P<issue_number>[\w-]+)/(?P<localid>[\w-]+)\.(?P<format_identifier>[\w-]+)?$',  # noqa
        journal_views_compat.ArticleDetailRedirectView.as_view(),
        name="legacy_article_detail_culture"
    ),
    url(r'^culture/(?P<journal_code>[\w-]+)/(?P<issue_localid>[\w-]+)/(?P<localid>[\w-]+)\.(?P<format_identifier>[\w-]+)?$',  # noqa
        journal_views_compat.ArticleDetailRedirectView.as_view(),
        name="legacy_article_detail_culture_localidentifier"
    )
]

book_url_patterns = [
    url(r'^$', book_views_compat.BooksHomeRedirectView.as_view(),
        name='legacy_books_home'),
    url(r'^(?P<path>[\w]+)/index\.htm$', book_views_compat.CollectionRedirectView.as_view(),
        name='legacy_collection_home'),
    url(r'^(?P<path>[\w/]+)/index\.htm$', book_views_compat.BookRedirectView.as_view(),
        name='legacy_book'),
]


# Base legacy url patterns
# -----------------------------------------------------------------------------

urlpatterns = [
    url(r'^rss.xml$', RedirectRetroUrls.as_view(
        pattern_name="public:journal:latest_issues_rss",
        permanent=True
    )),
    url(r'^(?:(?P<lang>[\w-]{2})/)?', include([
        url(r'^index.html?$', RedirectRetroUrls.as_view(pattern_name='home', permanent=True)),
        url(r'^revue/?$', RedirectRetroUrls.as_view(
            pattern_name='public:journal:journal_list',
            permanent=True)),
        url(r'^culture/?$', RedirectRetroUrls.as_view(
            pattern_name='public:journal:journal_list',
            permanent=True)),
        url(r'^abonnement/login\.jsp$',
            RedirectRetroUrls.as_view(pattern_name='login', permanent=True)),
        url(r'^abonnement/oublierPassword\.jsp$',
            RedirectRetroUrls.as_view(pattern_name='password_reset', permanent=True)),
        url(r'^abonnement/modifierPassword\.jsp$',
            RedirectRetroUrls.as_view(pattern_name='password_change', permanent=True)),

        url(r'^recherche/', include(search_url_patterns, namespace="legacy_search")),
        url(r'^these/', include(thesis_url_patterns, namespace="legacy_thesis")),
        url(r'^livre/', include(book_url_patterns, namespace="legacy_book")),
        url(r'^', include(journal_url_patterns, namespace="legacy_journal")),
        url(r'^', include(public_url_patterns)),
    ]),),
]
