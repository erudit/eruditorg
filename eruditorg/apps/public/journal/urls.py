# -*- coding: utf-8 -*-

from django.urls import include, re_path
from django.utils.translation import gettext_lazy as _
from django.views.decorators.clickjacking import xframe_options_exempt

from . import feeds
from . import views
from . import views_compat

journal_urlpatterns = (
    [
        re_path(_(r"^revues/$"), views.JournalListView.as_view(), name="journal_list"),
        re_path(_(r"^rss\.xml$"), feeds.LatestIssuesFeed(), name="latest_issues_rss"),
        # Statistic page for total and per journal number of articles.
        re_path(
            _(r"^revues/statistiques/$"), views.JournalStatisticsView.as_view(), name="statistics"
        ),
        # Journal URLs
        re_path(
            _(r"^revues/(?P<code>[\w-]+)/"),
            include(
                [
                    re_path(r"^$", views.JournalDetailView.as_view(), name="journal_detail"),
                    re_path(
                        _(r"^logo\.jpg$"), views.JournalRawLogoView.as_view(), name="journal_logo"
                    ),
                    re_path(
                        _(r"^auteurs/$"),
                        views.JournalAuthorsListView.as_view(),
                        name="journal_authors_list",
                    ),
                    re_path(
                        r"^rss\.xml$",
                        feeds.LatestJournalArticlesFeed(),
                        name="journal_articles_rss",
                    ),
                ]
            ),
        ),
        # Issue URLs
        re_path(
            _(
                r"^revues/(?P<journal_code>[\w-]+)/(?P<issue_slug>[\w-]*)-(?P<localidentifier>[\w-]+)/"  # noqa
            ),
            include(
                [
                    re_path(r"^$", views.IssueDetailView.as_view(), name="issue_detail"),
                    re_path(
                        _(r"^coverpage\.jpg$"),
                        views.IssueRawCoverpageView.as_view(),
                        name="issue_coverpage",
                    ),
                    re_path(
                        _(r"^coverpage-hd\.jpg$"),
                        views.IssueRawCoverpageHDView.as_view(),
                        name="issue_coverpage_hd",
                    ),
                    re_path(
                        _(r"^feuilletage/"),
                        include(
                            [
                                re_path(
                                    r"^$", views.IssueReaderView.as_view(), name="issue_reader"
                                ),
                                re_path(
                                    r"^(?P<page>[\d]+).jpg$",
                                    views.IssueReaderPageView.as_view(),
                                    name="issue_reader_page",
                                ),
                            ]
                        ),
                    ),
                ]
            ),
        ),
        re_path(
            _(
                r"^revues/(?P<journal_code>[\w-]+)/(?P<issue_slug>[\w-]*)-(?P<localidentifier>[\w-]+)"  # noqa
            ),
            include(
                [
                    re_path(r"^\.xml$", views.IssueXmlView.as_view(), name="issue_raw_xml"),
                ]
            ),
        ),
        # Article URLs
        re_path(
            _(
                r"^revues/(?P<journal_code>[\w-]+)/(?P<issue_slug>[\w-]*)-(?P<issue_localid>[\w-]+)/(?P<localid>[\w-]+)/"  # noqa
            ),
            include(
                [
                    re_path(r"^$", views.ArticleDetailView.as_view(), name="article_detail"),
                    re_path(
                        _(r"^resume/$"), views.ArticleSummaryView.as_view(), name="article_summary"
                    ),
                    re_path(
                        _(r"^biblio/$"), views.ArticleBiblioView.as_view(), name="article_biblio"
                    ),
                    re_path(_(r"^plan/$"), views.ArticleTocView.as_view(), name="article_toc"),
                    re_path(
                        _(r"^media/(?P<media_localid>[\.\w-]+)$"),
                        views.ArticleMediaView.as_view(),
                        name="article_media",
                    ),
                    re_path(
                        _(r"^premierepage\.pdf$"),
                        xframe_options_exempt(views.ArticleRawPdfFirstPageView.as_view()),
                        name="article_raw_pdf_firstpage",
                    ),
                    re_path(
                        r"^citation\.enw$",
                        views.ArticleEnwCitationView.as_view(),
                        name="article_citation_enw",
                    ),
                    re_path(
                        r"^citation\.ris$",
                        views.ArticleRisCitationView.as_view(),
                        name="article_citation_ris",
                    ),
                    re_path(
                        r"^citation\.bib$",
                        views.ArticleBibCitationView.as_view(),
                        name="article_citation_bib",
                    ),
                    re_path(
                        r"^ajax-citation-modal$",
                        views.ArticleAjaxCitationModalView.as_view(),
                        name="article_ajax_citation_modal",
                    ),
                ]
            ),
        ),
        re_path(
            _(
                r"^revues/(?P<journal_code>[\w-]+)/(?P<issue_slug>[\w-]*)-(?P<issue_localid>[\w-]+)/(?P<localid>[\w-]+)"  # noqa
            ),
            include(
                [
                    re_path(r"^\.html$", views_compat.ArticleDetailRedirectView.as_view()),
                    re_path(r"^\.xml$", views.ArticleXmlView.as_view(), name="article_raw_xml"),
                    re_path(
                        r"^\.pdf$",
                        xframe_options_exempt(views.ArticleRawPdfView.as_view()),
                        name="article_raw_pdf",
                    ),
                    re_path(r"^\.enw$", views.ArticleEnwCitationView.as_view(), name="article_enw"),
                    re_path(r"^\.ris$", views.ArticleRisCitationView.as_view(), name="article_ris"),
                    re_path(r"^\.bib$", views.ArticleBibCitationView.as_view(), name="article_bib"),
                ]
            ),
        ),
        re_path(
            r"^iderudit/(?P<localid>[\w-]+)/$",
            views.IdEruditArticleRedirectView.as_view(),
            name="iderudit_article_detail",
        ),
        # Redirect URLs
        re_path(
            _(r"^redirection/"),
            include(
                [
                    re_path(
                        _(r"^revue/(?P<code>[\w-]+)/$"),
                        views.JournalExternalURLRedirectView.as_view(),
                        name="journal_external_redirect",
                    ),
                    re_path(
                        _(r"^numero/(?P<localidentifier>[\w-]+)/$"),
                        views.IssueExternalURLRedirectView.as_view(),
                        name="issue_external_redirect",
                    ),
                ]
            ),
        ),
    ],
    "journal",
)

google_scholar_urlpatterns = (
    [
        re_path(
            r"^subscribers\.xml$", views.GoogleScholarSubscribersView.as_view(), name="subscribers"
        ),
        re_path(
            r"^subscriber_journals\.xml$",
            views.GoogleScholarSubscriberJournalsView.as_view(),
            name="subscriber_journals_erudit",
        ),
        re_path(
            r"^subscriber_journals_(?P<subscription_id>[0-9]+)\.xml$",
            views.GoogleScholarSubscriberJournalsView.as_view(),
            name="subscriber_journals",
        ),
    ],
    "google_scholar",
)
