# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.conf.urls import include

from .views import RedirectRetroUrls
from apps.public.journal import views_compat as journal_views_compat
from apps.public.book import views_compat as book_views_compat

# Thesis url patterns
# -----------------------------------------------------------------------------

thesis_url_patterns = ([
    url(r'^$', RedirectRetroUrls.as_view(
        pattern_name='public:thesis:home',
        permanent=True)),
    url(r'^liste.html?$', RedirectRetroUrls.as_view(
        pattern_name='public:thesis:home',
        permanent=True
    )),
    url(r'^index\.html?$', RedirectRetroUrls.as_view(
        pattern_name='public:thesis:home',
        permanent=True
    )),

], 'legacy_thesis')

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

search_url_patterns = ([
    url(r'^index\.html?$',
        RedirectRetroUrls.as_view(pattern_name='public:search:advanced_search', permanent=True))
], 'legacy_search')

# Journal legacy patterns
# ------------------------------------------------------------------------------

journal_url_patterns = ([
    # Journal
    url(r'^revue/(?P<code>[\w-]+)/?$',
        journal_views_compat.JournalDetailCheckRedirectView.as_view(
            pattern_name='public:journal:journal_detail', permanent=True),
        name="legacy_journal_detail"),
    url(r'^revue/(?P<code>[\w-]+)/auteurs\.html?$',
        journal_views_compat.JournalDetailCheckRedirectView.as_view(
            pattern_name='public:journal:journal_authors_list', permanent=True),
        name="legacy_journal_authors"),
    url(r'^revue/(?P<code>[\w-]+)/\w+\.html?$',
        journal_views_compat.JournalDetailCheckRedirectView.as_view(
            pattern_name='public:journal:journal_detail', permanent=True),
        name="legacy_journal_detail_index"),
    url(r'^revue/(?P<code>[\w-]+)/rss\.xml$',
        journal_views_compat.JournalDetailCheckRedirectView.as_view(
            pattern_name='public:journal:journal_articles_rss', permanent=True),
        name="legacy_journal_rss"),
    url(r'^culture/(?P<code>[\w-]+)/?$',
        journal_views_compat.JournalDetailCheckRedirectView.as_view(
            pattern_name='public:journal:journal_detail', permanent=True),
        name="legacy_journal_detail_culture"),
    url(r'^culture/(?P<code>[\w-]+)/auteurs\.html?$',
        journal_views_compat.JournalDetailCheckRedirectView.as_view(
            pattern_name='public:journal:journal_authors_list', permanent=True),
        name="legacy_journal_authors_culture"),
    url(r'^culture/(?P<code>[\w-]+)/\w+\.html?$',
        journal_views_compat.JournalDetailCheckRedirectView.as_view(
            pattern_name='public:journal:journal_detail', permanent=True),
        name="legacy_journal_detail_culture_index"),
    url(r'^culture/(?P<code>[\w-]+)/rss\.xml$',
        journal_views_compat.JournalDetailCheckRedirectView.as_view(
            pattern_name='public:journal:journal_articles_rss', permanent=True),
        name="legacy_journal_rss_culture"),

    # Issue
    url(r'^revue/(?P<journal_code>[\w-]+)/(?P<year>\d{4})/v(?P<v>[\w-]*)/n(?P<n>[\w-]*)/?$',  # noqa
        journal_views_compat.IssueDetailRedirectView.as_view(),
        name="legacy_issue_detail"),
    url(r'^revue/(?P<journal_code>[\w-]+)/(?P<year>\d{4})/v(?P<v>[\w-]*)/n(?P<n>[\w-]*)/index\.html?$',  # noqa
        journal_views_compat.IssueDetailRedirectView.as_view(),
        name="legacy_issue_detail_index"),
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

    # Issue coverpage
    url(r'^revue/(?P<journal_code>[\w-]+)/(?P<year>\d{4})/v(?P<v>[\w-]*)/n(?P<n>[\w-]*)/coverpage\.jpg?$',  # noqa
        journal_views_compat.IssueDetailRedirectView.as_view(
            pattern_name="public:journal:issue_coverpage",
        ), name="legacy_issue_coverpage"),
    url(r'^revue/(?P<journal_code>[\w-]+)/(?P<year>\d{4})/v(?P<v>[\w-]*)/n(?P<n>[\w-]*)/coverpageHD\.jpg?$',  # noqa
        journal_views_compat.IssueDetailRedirectView.as_view(
            pattern_name="public:journal:issue_coverpage_hd",
        ), name="legacy_issue_coverpage_hd"),
    url(r'^culture/(?P<journal_code>[\w-]+)/(?P<year>\d{4})/v(?P<v>[\w-]*)/(?P<localidentifier>[\w-]+)/coverpage\.jpg?$',  # noqa
        journal_views_compat.IssueDetailRedirectView.as_view(
            pattern_name="public:journal:issue_coverpage",
        ), name="legacy_issue_coverpage_culture_year_volume"),
    url(r'^culture/(?P<journal_code>[\w-]+)/(?P<year>\d{4})/v(?P<v>[\w-]*)/(?P<localidentifier>[\w-]+)/coverpageHD\.jpg?$',  # noqa
        journal_views_compat.IssueDetailRedirectView.as_view(
            pattern_name="public:journal:issue_coverpage_hd",
        ), name="legacy_issue_coverpage_hd_culture_year_volume"),
    url(r'^culture/(?P<journal_code>[\w-]+)/(?P<localidentifier>[\w-]+)/coverpage\.jpg?$',
        journal_views_compat.IssueDetailRedirectView.as_view(
            pattern_name="public:journal:issue_coverpage",
        ), name="legacy_issue_coverpage_culture"),
    url(r'^culture/(?P<journal_code>[\w-]+)/(?P<localidentifier>[\w-]+)/coverpageHD\.jpg?$',
        journal_views_compat.IssueDetailRedirectView.as_view(
            pattern_name="public:journal:issue_coverpage_hd",
        ), name="legacy_issue_coverpage_hd_culture"),

    # Article
    url(r'^revue/(?P<journal_code>[\w-]+)/(?P<year>\d{4})/v(?P<v>[\w-]*)/n(?P<issue_number>[\w-]*)/(?P<localid>[\w-]+)\.(?P<format_identifier>[\w-]+)?$',  # noqa
        journal_views_compat.ArticleDetailRedirectView.as_view(),
        name="legacy_article_detail",
    ),
    url(r'^iderudit/(?P<localid>[\w-]+)$',
        journal_views_compat.ArticleDetailRedirectView.as_view(),
        name="legacy_article_id",
    ),
    url(r'^culture/(?P<journal_code>[\w-]+)/(?P<year>\d{4})/v(?P<v>[\w-]*)/n(?P<issue_number>[\w-]*)/(?P<localid>[\w-]+)\.(?P<format_identifier>[\w-]+)?$',  # noqa
        journal_views_compat.ArticleDetailRedirectView.as_view(),
        name="legacy_article_detail_culture"
    ),
    url(r'^culture/(?P<journal_code>[\w-]+)/(?P<issue_localid>[\w-]+)/(?P<localid>[\w-]+)\.(?P<format_identifier>[\w-]+)?$',  # noqa
        journal_views_compat.ArticleDetailRedirectView.as_view(),
        name="legacy_article_detail_culture_localidentifier"
    )
], 'legacy_journal')

book_url_patterns = ([
    url(r'^$', book_views_compat.BooksHomeRedirectView.as_view(),
        name='legacy_books_home'),
    url(r'^(?P<collection>[\w-]+)/index\.htm$', book_views_compat.CollectionRedirectView.as_view(),
        name='legacy_collection_home'),
    url(r'^(?P<collection>[\w-]+)/(?P<book>[\w/-]+)/index\.htm$', book_views_compat.BookRedirectView.as_view(),  # noqa
        name='legacy_book'),
    url(r'^(?P<collection>[\w-]+)/(?P<book>[\w/-]+)/(?P<chapter_id>\w+)/?$', book_views_compat.ChapterRedirectView.as_view(),  # noqa
        name='legacy_chapter'),
    url(r'^(?P<collection>[\w-]+)/(?P<book>[\w/-]+)/(?P<chapter_id>\w+)\.(?P<pdf>pdf)$', book_views_compat.ChapterRedirectView.as_view(),  # noqa
        name='legacy_chapter_pdf'),
], 'legacy_book')


# Base legacy url patterns
# -----------------------------------------------------------------------------

urlpatterns = [
    url(r'^rss.xml$', RedirectRetroUrls.as_view(
        pattern_name="public:journal:latest_issues_rss",
        permanent=True
    )),
    url(r'^(?:(?P<lang>[\w-]{2})/)?', include([
        url(r'^index\.html?$', RedirectRetroUrls.as_view(pattern_name='public:home',
                                                         permanent=True)),
        url(r'^revue/?$', RedirectRetroUrls.as_view(
            pattern_name='public:journal:journal_list',
            permanent=True), name='legacy_journals'),
        url(r'^revue/index\.html?$', RedirectRetroUrls.as_view(
            pattern_name='public:journal:journal_list',
            permanent=True), name='legacy_journals_index'),
        url(r'^culture/?$', RedirectRetroUrls.as_view(
            pattern_name='public:journal:journal_list',
            permanent=True), name='legacy_journals_culture'),
        url(r'^culture/index\.html?$', RedirectRetroUrls.as_view(
            pattern_name='public:journal:journal_list',
            permanent=True), name='legacy_journals_culture_index'),
        url(r'^abonnement/login\.jsp$',
            RedirectRetroUrls.as_view(pattern_name='login', permanent=True)),
        url(r'^abonnement/oublierPassword\.jsp$',
            RedirectRetroUrls.as_view(pattern_name='password_reset', permanent=True)),
        url(r'^abonnement/modifierPassword\.jsp$',
            RedirectRetroUrls.as_view(pattern_name='password_change', permanent=True)),

        url(r'^recherche/', include(search_url_patterns)),
        url(r'^these/', include(thesis_url_patterns)),
        url(r'^livre/', include(book_url_patterns)),
        url(r'^', include(journal_url_patterns)),
        url(r'^', include(public_url_patterns)),
    ]),),
]
