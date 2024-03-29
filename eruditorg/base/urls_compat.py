# -*- coding: utf-8 -*-

from django.urls import include, re_path

from .views import RedirectRetroUrls
from apps.public.journal import views_compat as journal_views_compat
from apps.public.book import views_compat as book_views_compat

# Thesis re_path patterns
# -----------------------------------------------------------------------------

thesis_url_patterns = (
    [
        re_path(r"^$", RedirectRetroUrls.as_view(pattern_name="public:thesis:home")),
        re_path(r"^liste.html?$", RedirectRetroUrls.as_view(pattern_name="public:thesis:home")),
        re_path(r"^index\.html?$", RedirectRetroUrls.as_view(pattern_name="public:thesis:home")),
    ],
    "legacy_thesis",
)

# Public legacy patterns
# -----------------------------------------------------------------------------

public_url_patterns = [
    re_path(r"^client/login.jsp$", RedirectRetroUrls.as_view(pattern_name="public:auth:login")),
    re_path(
        r"^client/getNewPassword.jsp$",
        RedirectRetroUrls.as_view(pattern_name="public:auth:password_reset"),
    ),
    re_path(
        r"^client/updatePassword.jsp$",
        RedirectRetroUrls.as_view(pattern_name="public:auth:password_change"),
    ),
]

# Search legacy patterns
# -----------------------------------------------------------------------------

search_url_patterns = (
    [
        re_path(
            r"^index\.html?$",
            RedirectRetroUrls.as_view(pattern_name="public:search:advanced_search"),
        )
    ],
    "legacy_search",
)

# Journal legacy patterns
# ------------------------------------------------------------------------------

journal_url_patterns = (
    [
        # Journal
        re_path(
            r"^revue/(?P<code>[\w-]+)/?$",
            journal_views_compat.JournalDetailCheckRedirectView.as_view(
                pattern_name="public:journal:journal_detail"
            ),
            name="legacy_journal_detail",
        ),
        re_path(
            r"^revue/(?P<code>[\w-]+)/auteurs\.html?$",
            journal_views_compat.JournalDetailCheckRedirectView.as_view(
                pattern_name="public:journal:journal_authors_list"
            ),
            name="legacy_journal_authors",
        ),
        re_path(
            r"^revue/(?P<code>[\w-]+)/\w+\.html?$",
            journal_views_compat.JournalDetailCheckRedirectView.as_view(
                pattern_name="public:journal:journal_detail"
            ),
            name="legacy_journal_detail_index",
        ),
        re_path(
            r"^revue/(?P<code>[\w-]+)/rss\.xml$",
            journal_views_compat.JournalDetailCheckRedirectView.as_view(
                pattern_name="public:journal:journal_articles_rss"
            ),
            name="legacy_journal_rss",
        ),
        re_path(
            r"^culture/(?P<code>[\w-]+)/?$",
            journal_views_compat.JournalDetailCheckRedirectView.as_view(
                pattern_name="public:journal:journal_detail"
            ),
            name="legacy_journal_detail_culture",
        ),
        re_path(
            r"^culture/(?P<code>[\w-]+)/auteurs\.html?$",
            journal_views_compat.JournalDetailCheckRedirectView.as_view(
                pattern_name="public:journal:journal_authors_list"
            ),
            name="legacy_journal_authors_culture",
        ),
        re_path(
            r"^culture/(?P<code>[\w-]+)/\w+\.html?$",
            journal_views_compat.JournalDetailCheckRedirectView.as_view(
                pattern_name="public:journal:journal_detail"
            ),
            name="legacy_journal_detail_culture_index",
        ),
        re_path(
            r"^culture/(?P<code>[\w-]+)/rss\.xml$",
            journal_views_compat.JournalDetailCheckRedirectView.as_view(
                pattern_name="public:journal:journal_articles_rss"
            ),
            name="legacy_journal_rss_culture",
        ),
        # Issue
        re_path(
            r"^revue/(?P<journal_code>[\w-]+)/(?P<year>\d{4})/v(?P<v>[\w-]*)/n(?P<n>[\w-]*)/?$",
            journal_views_compat.IssueDetailRedirectView.as_view(),
            name="legacy_issue_detail",
        ),
        re_path(
            r"^revue/(?P<journal_code>[\w-]+)/(?P<year>\d{4})/v(?P<v>[\w-]*)/n(?P<n>[\w-]*)/index\.html?$",  # noqa
            journal_views_compat.IssueDetailRedirectView.as_view(),
            name="legacy_issue_detail_index",
        ),
        re_path(
            r"^culture/(?P<journal_code>[\w-]+)/(?P<year>\d{4})/v(?P<v>[\w-]*)/(?P<localidentifier>[\w-]+)/?$",  # noqa
            journal_views_compat.IssueDetailRedirectView.as_view(),
            name="legacy_issue_detail_culture_year_volume",
        ),
        re_path(
            r"^culture/(?P<journal_code>[\w-]+)/(?P<year>\d{4})/v(?P<v>[\w-]*)/(?P<localidentifier>[\w-]+)/[\w-]+\.html?$",  # noqa
            journal_views_compat.IssueDetailRedirectView.as_view(),
            name="legacy_issue_detail_culture_year_volume_index",
        ),
        re_path(
            r"^culture/(?P<journal_code>[\w-]+)/(?P<localidentifier>[\w-]+)/?$",
            journal_views_compat.IssueDetailRedirectView.as_view(),
            name="legacy_issue_detail_culture",
        ),
        re_path(
            r"^culture/(?P<journal_code>[\w-]+)/(?P<localidentifier>[\w-]+)/index\.html?$",
            journal_views_compat.IssueDetailRedirectView.as_view(),
            name="legacy_issue_detail_culture_index",
        ),
        # Issue coverpage
        re_path(
            r"^revue/(?P<journal_code>[\w-]+)/(?P<year>\d{4})/v(?P<v>[\w-]*)/n(?P<n>[\w-]*)/coverpage\.jpg?$",  # noqa
            journal_views_compat.IssueDetailRedirectView.as_view(
                pattern_name="public:journal:issue_coverpage",
            ),
            name="legacy_issue_coverpage",
        ),
        re_path(
            r"^revue/(?P<journal_code>[\w-]+)/(?P<year>\d{4})/v(?P<v>[\w-]*)/n(?P<n>[\w-]*)/coverpageHD\.jpg?$",  # noqa
            journal_views_compat.IssueDetailRedirectView.as_view(
                pattern_name="public:journal:issue_coverpage_hd",
            ),
            name="legacy_issue_coverpage_hd",
        ),
        re_path(
            r"^culture/(?P<journal_code>[\w-]+)/(?P<year>\d{4})/v(?P<v>[\w-]*)/(?P<localidentifier>[\w-]+)/coverpage\.jpg?$",  # noqa
            journal_views_compat.IssueDetailRedirectView.as_view(
                pattern_name="public:journal:issue_coverpage",
            ),
            name="legacy_issue_coverpage_culture_year_volume",
        ),
        re_path(
            r"^culture/(?P<journal_code>[\w-]+)/(?P<year>\d{4})/v(?P<v>[\w-]*)/(?P<localidentifier>[\w-]+)/coverpageHD\.jpg?$",  # noqa
            journal_views_compat.IssueDetailRedirectView.as_view(
                pattern_name="public:journal:issue_coverpage_hd",
            ),
            name="legacy_issue_coverpage_hd_culture_year_volume",
        ),
        re_path(
            r"^culture/(?P<journal_code>[\w-]+)/(?P<localidentifier>[\w-]+)/coverpage\.jpg?$",
            journal_views_compat.IssueDetailRedirectView.as_view(
                pattern_name="public:journal:issue_coverpage",
            ),
            name="legacy_issue_coverpage_culture",
        ),
        re_path(
            r"^culture/(?P<journal_code>[\w-]+)/(?P<localidentifier>[\w-]+)/coverpageHD\.jpg?$",
            journal_views_compat.IssueDetailRedirectView.as_view(
                pattern_name="public:journal:issue_coverpage_hd",
            ),
            name="legacy_issue_coverpage_hd_culture",
        ),
        # Article
        re_path(
            r"^revue/(?P<journal_code>[\w-]+)/(?P<year>\d{4})/v(?P<v>[\w-]*)/n(?P<issue_number>[\w-]*)/(?P<localid>[\w-]+)\.(?P<format_identifier>[\w-]+)?$",  # noqa
            journal_views_compat.ArticleDetailRedirectView.as_view(),
            name="legacy_article_detail",
        ),
        re_path(
            r"^iderudit/(?P<localid>[\w-]+)$",
            journal_views_compat.ArticleDetailRedirectView.as_view(),
            name="legacy_article_id",
        ),
        re_path(
            r"^culture/(?P<journal_code>[\w-]+)/(?P<year>\d{4})/v(?P<v>[\w-]*)/n(?P<issue_number>[\w-]*)/(?P<localid>[\w-]+)\.(?P<format_identifier>[\w-]+)?$",  # noqa
            journal_views_compat.ArticleDetailRedirectView.as_view(),
            name="legacy_article_detail_culture",
        ),
        re_path(
            r"^culture/(?P<journal_code>[\w-]+)/(?P<issue_localid>[\w-]+)/(?P<localid>[\w-]+)\.(?P<format_identifier>[\w-]+)?$",  # noqa
            journal_views_compat.ArticleDetailRedirectView.as_view(),
            name="legacy_article_detail_culture_localidentifier",
        ),
    ],
    "legacy_journal",
)

book_url_patterns = (
    [
        re_path(r"^$", book_views_compat.BooksHomeRedirectView.as_view(), name="legacy_books_home"),
        re_path(
            r"^(?P<collection>[\w-]+)/index\.htm$",
            book_views_compat.CollectionRedirectView.as_view(),
            name="legacy_collection_home",
        ),
        re_path(
            r"^(?P<collection>[\w-]+)/(?P<book>[\w/-]+)/index\.htm$",
            book_views_compat.BookRedirectView.as_view(),
            name="legacy_book",
        ),
        re_path(
            r"^(?P<collection>[\w-]+)/(?P<book>[\w/-]+)/(?P<chapter_id>\w+)/?$",
            book_views_compat.ChapterRedirectView.as_view(),
            name="legacy_chapter",
        ),
        re_path(
            r"^(?P<collection>[\w-]+)/(?P<book>[\w/-]+)/(?P<chapter_id>\w+)\.(?P<pdf>pdf)$",
            book_views_compat.ChapterRedirectView.as_view(),
            name="legacy_chapter_pdf",
        ),
    ],
    "legacy_book",
)


# Base legacy re_path patterns
# -----------------------------------------------------------------------------

urlpatterns = [
    re_path(
        r"^rss.xml$",
        RedirectRetroUrls.as_view(
            pattern_name="public:journal:latest_issues_rss",
        ),
    ),
    re_path(
        r"^(?:(?P<lang>[\w-]{2})/)?",
        include(
            [
                re_path(r"^index\.html?$", RedirectRetroUrls.as_view(pattern_name="public:home")),
                re_path(
                    r"^revue/?$",
                    RedirectRetroUrls.as_view(pattern_name="public:journal:journal_list"),
                    name="legacy_journals",
                ),
                re_path(
                    r"^revue/index\.html?$",
                    RedirectRetroUrls.as_view(pattern_name="public:journal:journal_list"),
                    name="legacy_journals_index",
                ),
                re_path(
                    r"^culture/?$",
                    RedirectRetroUrls.as_view(pattern_name="public:journal:journal_list"),
                    name="legacy_journals_culture",
                ),
                re_path(
                    r"^culture/index\.html?$",
                    RedirectRetroUrls.as_view(pattern_name="public:journal:journal_list"),
                    name="legacy_journals_culture_index",
                ),
                re_path(
                    r"^abonnement/login\.jsp$",
                    RedirectRetroUrls.as_view(pattern_name="public:auth:login"),
                ),
                re_path(
                    r"^abonnement/oublierPassword\.jsp$",
                    RedirectRetroUrls.as_view(pattern_name="public:auth:password_reset"),
                ),
                re_path(
                    r"^abonnement/modifierPassword\.jsp$",
                    RedirectRetroUrls.as_view(pattern_name="public:auth:password_change"),
                ),
                re_path(r"^recherche/", include(search_url_patterns)),
                re_path(r"^these/", include(thesis_url_patterns)),
                re_path(r"^livre/", include(book_url_patterns)),
                re_path(r"^", include(journal_url_patterns)),
                re_path(r"^", include(public_url_patterns)),
            ]
        ),
    ),
]
