# -*- coding: utf-8 -*-

from django.conf.urls import include
from django.conf.urls import url
from django.utils.translation import gettext_lazy as _
from django.views.decorators.clickjacking import xframe_options_exempt

from . import feeds
from . import views
from . import views_compat

journal_urlpatterns = (
    [
        url(_(r"^revues/$"), views.JournalListView.as_view(), name="journal_list"),
        url(_(r"^rss\.xml$"), feeds.LatestIssuesFeed(), name="latest_issues_rss"),
        # Statistic page for total and per journal number of articles.
        url(_(r"^revues/statistiques/$"), views.JournalStatisticsView.as_view(), name="statistics"),
        # Journal URLs
        url(
            _(r"^revues/(?P<code>[\w-]+)/"),
            include(
                [
                    url(r"^$", views.JournalDetailView.as_view(), name="journal_detail"),
                    url(_(r"^logo\.jpg$"), views.JournalRawLogoView.as_view(), name="journal_logo"),
                    url(
                        _(r"^auteurs/$"),
                        views.JournalAuthorsListView.as_view(),
                        name="journal_authors_list",
                    ),
                    url(
                        r"^rss\.xml$",
                        feeds.LatestJournalArticlesFeed(),
                        name="journal_articles_rss",
                    ),
                ]
            ),
        ),
        # Issue URLs
        url(
            _(
                r"^revues/(?P<journal_code>[\w-]+)/(?P<issue_slug>[\w-]*)-(?P<localidentifier>[\w-]+)/"  # noqa
            ),
            include(
                [
                    url(r"^$", views.IssueDetailView.as_view(), name="issue_detail"),
                    url(
                        _(r"^coverpage\.jpg$"),
                        views.IssueRawCoverpageView.as_view(),
                        name="issue_coverpage",
                    ),
                    url(
                        _(r"^coverpage-hd\.jpg$"),
                        views.IssueRawCoverpageHDView.as_view(),
                        name="issue_coverpage_hd",
                    ),
                    url(
                        _(r"^feuilletage/"),
                        include(
                            [
                                url(r"^$", views.IssueReaderView.as_view(), name="issue_reader"),
                                url(
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
        url(
            _(
                r"^revues/(?P<journal_code>[\w-]+)/(?P<issue_slug>[\w-]*)-(?P<localidentifier>[\w-]+)"  # noqa
            ),
            include(
                [
                    url(r"^\.xml$", views.IssueXmlView.as_view(), name="issue_raw_xml"),
                ]
            ),
        ),
        # Article URLs
        url(
            _(
                r"^revues/(?P<journal_code>[\w-]+)/(?P<issue_slug>[\w-]*)-(?P<issue_localid>[\w-]+)/(?P<localid>[\w-]+)/"  # noqa
            ),
            include(
                [
                    url(r"^$", views.ArticleDetailView.as_view(), name="article_detail"),
                    url(
                        _(r"^resume/$"), views.ArticleSummaryView.as_view(), name="article_summary"
                    ),
                    url(_(r"^biblio/$"), views.ArticleBiblioView.as_view(), name="article_biblio"),
                    url(_(r"^plan/$"), views.ArticleTocView.as_view(), name="article_toc"),
                    url(
                        _(r"^media/(?P<media_localid>[\.\w-]+)$"),
                        views.ArticleMediaView.as_view(),
                        name="article_media",
                    ),
                    url(
                        _(r"^premierepage\.pdf$"),
                        xframe_options_exempt(views.ArticleRawPdfFirstPageView.as_view()),
                        name="article_raw_pdf_firstpage",
                    ),
                    url(
                        r"^citation\.enw$",
                        views.ArticleEnwCitationView.as_view(),
                        name="article_citation_enw",
                    ),
                    url(
                        r"^citation\.ris$",
                        views.ArticleRisCitationView.as_view(),
                        name="article_citation_ris",
                    ),
                    url(
                        r"^citation\.bib$",
                        views.ArticleBibCitationView.as_view(),
                        name="article_citation_bib",
                    ),
                ]
            ),
        ),
        url(
            _(
                r"^revues/(?P<journal_code>[\w-]+)/(?P<issue_slug>[\w-]*)-(?P<issue_localid>[\w-]+)/(?P<localid>[\w-]+)"  # noqa
            ),
            include(
                [
                    url(r"^\.html$", views_compat.ArticleDetailRedirectView.as_view()),
                    url(r"^\.xml$", views.ArticleXmlView.as_view(), name="article_raw_xml"),
                    url(
                        r"^\.pdf$",
                        xframe_options_exempt(views.ArticleRawPdfView.as_view()),
                        name="article_raw_pdf",
                    ),
                    url(r"^\.enw$", views.ArticleEnwCitationView.as_view(), name="article_enw"),
                    url(r"^\.ris$", views.ArticleRisCitationView.as_view(), name="article_ris"),
                    url(r"^\.bib$", views.ArticleBibCitationView.as_view(), name="article_bib"),
                ]
            ),
        ),
        url(
            r"^iderudit/(?P<localid>[\w-]+)/$",
            views.IdEruditArticleRedirectView.as_view(),
            name="iderudit_article_detail",
        ),
        # Redirect URLs
        url(
            _(r"^redirection/"),
            include(
                [
                    url(
                        _(r"^revue/(?P<code>[\w-]+)/$"),
                        views.JournalExternalURLRedirectView.as_view(),
                        name="journal_external_redirect",
                    ),
                    url(
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
        url(
            r"^subscribers\.xml$", views.GoogleScholarSubscribersView.as_view(), name="subscribers"
        ),
        url(
            r"^subscriber_journals\.xml$",
            views.GoogleScholarSubscriberJournalsView.as_view(),
            name="subscriber_journals_erudit",
        ),
        url(
            r"^subscriber_journals_(?P<subscription_id>[0-9]+)\.xml$",
            views.GoogleScholarSubscriberJournalsView.as_view(),
            name="subscriber_journals",
        ),
    ],
    "google_scholar",
)
