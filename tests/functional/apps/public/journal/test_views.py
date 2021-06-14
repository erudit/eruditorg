from bs4 import BeautifulSoup
from collections import OrderedDict
from lxml import etree as et

import datetime as dt
import io
import os
import fitz
import unittest.mock
import itertools
from hashlib import md5

from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.http.response import HttpResponseRedirect
from django.test import Client
from django.test import RequestFactory
from django.conf import settings
from django.test.utils import override_settings
from eruditarticle.objects.publication import SummaryArticle
import pytest

from apps.public.journal.viewmixins import SolrDataMixin
from core.subscription.test.utils import generate_casa_token
from erudit.models import JournalType, Issue, Article
from erudit.test.factories import ArticleFactory
from erudit.test.factories import CollectionFactory
from erudit.test.factories import DisciplineFactory
from erudit.test.factories import IssueFactory
from erudit.test.factories import EmbargoedIssueFactory
from erudit.test.factories import OpenAccessIssueFactory
from erudit.test.factories import JournalFactory
from erudit.test.factories import JournalInformationFactory
from erudit.test.solr import FakeSolrData
from erudit.fedora import repository

from base.test.factories import UserFactory
from core.subscription.test.factories import JournalAccessSubscriptionFactory
from core.subscription.models import UserSubscriptions
from core.metrics.conf import settings as metrics_settings

from apps.public.journal.views import ArticleMediaView
from apps.public.journal.views import ArticleRawPdfView
from apps.public.journal.views import ArticleRawPdfFirstPageView
from collections import namedtuple

FIXTURE_ROOT = os.path.join(os.path.dirname(__file__), "fixtures")


pytestmark = pytest.mark.django_db


def journal_detail_url(journal):
    return reverse("public:journal:journal_detail", kwargs={"code": journal.code})


def issue_detail_url(issue):
    return reverse(
        "public:journal:issue_detail",
        args=[issue.journal.code, issue.volume_slug, issue.localidentifier],
    )


def journal_authors_list_url(journal):
    return reverse(
        "public:journal:journal_authors_list",
        args=[journal.code],
    )


def article_detail_url(article):
    return reverse(
        "public:journal:article_detail",
        kwargs={
            "journal_code": article.issue.journal.code,
            "issue_slug": article.issue.volume_slug,
            "issue_localid": article.issue.localidentifier,
            "localid": article.localidentifier,
        },
    )


def article_raw_pdf_url(article):
    issue = article.issue
    journal_id = issue.journal.localidentifier
    issue_id = issue.localidentifier
    article_id = article.localidentifier
    return reverse(
        "public:journal:article_raw_pdf", args=(journal_id, issue.volume_slug, issue_id, article_id)
    )


class TestJournalListView:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = Client()
        self.user = UserFactory.create(username="foobar")
        self.user.set_password("notsecret")
        self.user.save()

    def test_upcoming_journals_are_hidden_from_list(self):

        # Create 6 journals
        journals = JournalFactory.create_batch(6)

        # Create an issue for the first 5 journals
        for journal in journals[:5]:
            IssueFactory(journal=journal)

        url = reverse("public:journal:journal_list")
        # Run
        response = self.client.get(url)
        displayed_journals = set(response.context["journals"])
        assert displayed_journals == set(journals[:5])
        assert journals[5] not in displayed_journals

    def test_can_sort_journals_by_name(self):
        # Setup
        collection = CollectionFactory.create()
        journal_1 = JournalFactory.create_with_issue(collection=collection, name="ABC journal")
        journal_2 = JournalFactory.create_with_issue(collection=collection, name="ACD journal")
        journal_3 = JournalFactory.create_with_issue(collection=collection, name="DEF journal")
        journal_4 = JournalFactory.create_with_issue(collection=collection, name="GHI journal")
        journal_5 = JournalFactory.create_with_issue(collection=collection, name="GIJ journal")
        journal_6 = JournalFactory.create_with_issue(collection=collection, name="GJK journal")
        url = reverse("public:journal:journal_list")
        # Run
        response = self.client.get(url)
        # Check
        assert response.status_code == 200
        assert len(response.context["sorted_objects"]) == 3
        assert response.context["sorted_objects"][0]["key"] == "A"
        assert response.context["sorted_objects"][0]["objects"] == [
            journal_1,
            journal_2,
        ]
        assert response.context["sorted_objects"][1]["key"] == "D"
        assert response.context["sorted_objects"][1]["objects"] == [
            journal_3,
        ]
        assert response.context["sorted_objects"][2]["key"] == "G"
        assert response.context["sorted_objects"][2]["objects"] == [
            journal_4,
            journal_5,
            journal_6,
        ]

    def test_can_sort_journals_by_disciplines(self):
        # Setup
        collection = CollectionFactory.create()
        discipline_1 = DisciplineFactory.create(code="abc-discipline", name="ABC")
        discipline_2 = DisciplineFactory.create(code="def-discipline", name="DEF")
        discipline_3 = DisciplineFactory.create(code="ghi-discipline", name="GHI")
        journal_1 = JournalFactory.create_with_issue(collection=collection)
        journal_1.disciplines.add(discipline_1)
        journal_2 = JournalFactory.create_with_issue(collection=collection)
        journal_2.disciplines.add(discipline_1)
        journal_3 = JournalFactory.create_with_issue(collection=collection)
        journal_3.disciplines.add(discipline_2)
        journal_4 = JournalFactory.create_with_issue(collection=collection)
        journal_4.disciplines.add(discipline_3)
        journal_5 = JournalFactory.create_with_issue(collection=collection)
        journal_5.disciplines.add(discipline_3)
        journal_6 = JournalFactory.create_with_issue(collection=collection)
        journal_6.disciplines.add(discipline_3)
        url = reverse("public:journal:journal_list")
        # Run
        response = self.client.get(url, {"sorting": "disciplines"})
        # Check
        assert response.status_code == 200
        assert len(response.context["sorted_objects"]) == 3
        assert response.context["sorted_objects"][0]["key"] == discipline_1.code
        assert response.context["sorted_objects"][0]["collections"][0]["key"] == collection
        assert response.context["sorted_objects"][0]["collections"][0]["objects"] == [
            journal_1,
            journal_2,
        ]
        assert response.context["sorted_objects"][1]["key"] == discipline_2.code
        assert response.context["sorted_objects"][1]["collections"][0]["key"] == collection
        assert response.context["sorted_objects"][1]["collections"][0]["objects"] == [
            journal_3,
        ]
        assert response.context["sorted_objects"][2]["key"] == discipline_3.code
        assert response.context["sorted_objects"][2]["collections"][0]["key"] == collection
        assert set(response.context["sorted_objects"][2]["collections"][0]["objects"]) == set(
            [
                journal_4,
                journal_5,
                journal_6,
            ]
        )

    def test_only_main_collections_are_shown_by_default(self):
        collection = CollectionFactory.create()
        main_collection = CollectionFactory.create(is_main_collection=True)
        JournalFactory.create_with_issue(collection=collection)
        journal2 = JournalFactory.create_with_issue(collection=main_collection)
        url = reverse("public:journal:journal_list")
        response = self.client.get(url)

        assert list(response.context["journals"]) == [journal2]

    def test_can_filter_the_journals_by_open_access(self):
        # Setup
        collection = CollectionFactory.create()
        journal_1 = JournalFactory.create_with_issue(collection=collection, open_access=True)
        JournalFactory.create(collection=collection, open_access=False)
        url = reverse("public:journal:journal_list")
        # Run
        response = self.client.get(url, data={"open_access": True})
        # Check
        assert list(response.context["journals"]) == [
            journal_1,
        ]

    def test_can_filter_the_journals_by_types(self):
        # Setup
        collection = CollectionFactory.create()
        jtype_1 = JournalType.objects.create(code="T1", name="T1")
        jtype_2 = JournalType.objects.create(code="T2", name="T2")
        JournalFactory.create(collection=collection, type=jtype_1)
        journal_2 = JournalFactory.create_with_issue(collection=collection, type=jtype_2)
        url = reverse("public:journal:journal_list")
        # Run
        response = self.client.get(
            url,
            data={
                "types": [
                    "T2",
                ]
            },
        )
        # Check
        assert list(response.context["journals"]) == [
            journal_2,
        ]

    def test_can_filter_the_journals_by_collections(self):
        # Setup
        col_1 = CollectionFactory(code="col1")
        col_2 = CollectionFactory(code="col2")
        JournalFactory.create_with_issue(collection=col_1)
        journal_2 = JournalFactory.create_with_issue(collection=col_2)
        url = reverse("public:journal:journal_list")
        # Run
        response = self.client.get(
            url,
            data={
                "collections": [
                    "col2",
                ]
            },
        )
        # Check
        assert list(response.context["journals"]) == [
            journal_2,
        ]

    def test_can_filter_the_journals_by_disciplines(self):
        j1 = JournalFactory.create_with_issue(disciplines=["d1", "d2"])
        j2 = JournalFactory.create_with_issue(disciplines=["d2"])
        j3 = JournalFactory.create_with_issue(disciplines=["d3"])
        JournalFactory.create_with_issue(disciplines=["d4"])
        url = reverse("public:journal:journal_list")
        response = self.client.get(url, data={"disciplines": ["d2", "d3"]})
        assert set(response.context["journals"]) == {j1, j2, j3}

    def test_new_journal_titles_are_not_uppercased(self):
        JournalFactory(is_new=True, name="Enjeux et société")
        url = reverse("public:journal:journal_list")
        html = self.client.get(url).content.decode()
        dom = BeautifulSoup(html, "html.parser")
        journals_list = dom.find("div", {"class": "journals-list"})
        assert "Enjeux et société" in journals_list.decode()
        assert "Enjeux Et Société" not in journals_list.decode()

    def test_journal_year_of_addition_is_displayed(self):
        JournalFactory(is_new=True, year_of_addition="2020")
        url = reverse("public:journal:journal_list")
        html = self.client.get(url).content.decode()
        dom = BeautifulSoup(html, "html.parser")
        journals_list = dom.find("div", {"class": "journals-list"})
        assert "(nouveauté 2020)" in journals_list.decode()

    @pytest.mark.parametrize(
        "logo, expected_logo_display",
        [
            ("logo.png", True),
            (False, False),
        ],
    )
    def test_do_not_display_non_existent_journal_logo_on_list_per_disciplines(
        self,
        logo,
        expected_logo_display,
    ):
        journal = JournalFactory.create_with_issue(code="journal", name="Journal")
        journal.disciplines.add(DisciplineFactory())
        if logo:
            repository.api.register_datastream(
                journal.get_full_identifier(),
                "/LOGO/content",
                open(settings.MEDIA_ROOT + "/" + logo, "rb").read(),
            )
        url = reverse("public:journal:journal_list")

        html = self.client.get(url, {"sorting": "disciplines"}).content.decode()
        logo = (
            "<img\n                  "
            'src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQV'
            'R42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="\n                  '
            'data-src="/fr/revues/journal/logo.jpg"\n                  '
            'alt="Logo pour Inter"\n                  '
            'class="lazyload img-responsive card__figure"\n                '
            "/>"
        )
        if expected_logo_display:
            assert logo in html
        else:
            assert logo not in html


class TestJournalDetailView:
    @pytest.fixture(autouse=True)
    def setup(self, settings):
        settings.DEBUG = True
        self.client = Client()
        self.user = UserFactory.create(username="foobar")
        self.user.set_password("notsecret")
        self.user.save()

    def test_main_title_is_always_in_context(self):
        journal = JournalFactory()
        response = self.client.get(journal_detail_url(journal))
        assert "main_title" in response.context.keys()

    def test_can_embed_the_journal_information_in_the_context_if_available(self):
        # Setup
        journal_info = JournalInformationFactory(journal=JournalFactory())
        url_1 = journal_detail_url(journal_info.journal)
        journal_2 = JournalFactory()
        url_2 = journal_detail_url(journal_2)

        # Run
        response_1 = self.client.get(url_1)
        response_2 = self.client.get(url_2)

        # Check
        assert response_1.status_code == response_2.status_code == 200

        assert response_1.context["journal_info"] == journal_info
        assert response_2.context["journal_info"] is None

    def test_can_display_when_issues_have_a_space_in_their_number(self, monkeypatch):
        monkeypatch.setattr(Issue, "erudit_object", unittest.mock.MagicMock())
        issue = IssueFactory(number="2 bis")
        url_1 = journal_detail_url(issue.journal)
        # Run
        response_1 = self.client.get(url_1)
        assert response_1.status_code == 200

    def test_can_embed_the_published_issues_in_the_context(self):
        # Setup

        journal = JournalFactory(collection=CollectionFactory(localidentifier="erudit"))

        issue = IssueFactory(journal=journal)
        IssueFactory(journal=journal, is_published=False)

        url = journal_detail_url(journal)
        # Run
        response = self.client.get(url)
        # Check
        assert response.status_code == 200
        assert list(response.context["issues"]) == [issue]

    def test_can_embed_the_current_issue_in_the_context(self):
        issue1 = IssueFactory.create()
        issue2 = IssueFactory.create_published_after(issue1)

        url = journal_detail_url(issue1.journal)
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.context["current_issue"] == issue2

    def test_can_embed_the_current_issue_external_url_in_the_context(self):
        # If the latest issue has an external URL, it's link properly reflects that (proper href,
        # blank target.
        external_url = "https://example.com"
        issue1 = IssueFactory.create()
        issue2 = IssueFactory.create_published_after(issue1, external_url=external_url)

        url = journal_detail_url(issue1.journal)
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.context["current_issue"] == issue2
        link_attrs = response.context["current_issue"].extra.detail_link_attrs()
        assert external_url in link_attrs
        assert "_blank" in link_attrs

    def test_external_issues_are_never_locked(self):
        # when an issue has an external url, we never show a little lock icon next to it.
        external_url = "https://example.com"
        collection = CollectionFactory.create(code="erudit")
        journal = JournalFactory(open_access=False, collection=collection)  # embargoed
        issue1 = IssueFactory.create(journal=journal, external_url=external_url)

        url = journal_detail_url(issue1.journal)
        response = self.client.get(url)

        assert not response.context["current_issue"].extra.is_locked()

    def test_embeds_subscription_info_to_context(self):
        subscription = JournalAccessSubscriptionFactory(
            type="individual",
            user=self.user,
        )
        self.client.login(username="foobar", password="notsecret")
        url = journal_detail_url(subscription.journal_management_subscription.journal)
        response = self.client.get(url)
        assert response.status_code == 200
        assert response.context["content_access_granted"]
        assert response.context["subscription_type"] == "individual"

    def test_journal_detail_has_elements_for_anchors(self):
        issue = IssueFactory()
        url = journal_detail_url(issue.journal)
        response = self.client.get(url)
        content = response.content
        assert b'<li role="presentation"' in content
        assert b'<section role="tabpanel"' in content
        assert b'<li role="presentation" id="journal-info-about-li"' not in content
        assert (
            b'<section role="tabpanel" class="tab-pane journal-info-block" id="journal-info-about"'
            not in content
        )

    @pytest.mark.parametrize("charges_apc", (True, False))
    def test_journal_detail_has_no_apc_mention_if_it_charges_apc(self, charges_apc):
        journal = JournalFactory(charges_apc=charges_apc)
        url = journal_detail_url(journal)
        response = self.client.get(url)
        content = response.content

        if not charges_apc:
            assert b"Frais de publication" in content
        else:
            assert b"Frais de publication" not in content

    @pytest.mark.parametrize("localidentifier", ("journal", "previous_journal"))
    def test_journal_notes_with_previous_journal(self, localidentifier):
        journal = JournalFactory(
            localidentifier=localidentifier,
            notes=[
                {
                    "pid": "erudit:erudit.journal",
                    "langue": "fr",
                    "content": "Note pour journal",
                },
                {
                    "pid": "erudit:erudit.previous_journal",
                    "langue": "fr",
                    "content": "Note pour previous_journal",
                },
            ],
        )
        IssueFactory(journal=journal)
        html = self.client.get(journal_detail_url(journal)).content.decode()
        if localidentifier == "journal":
            assert "Note pour journal" in html
            assert "Note pour previous_journal" not in html
        elif localidentifier == "previous_journal":
            assert "Note pour journal" not in html
            assert "Note pour previous_journal" in html

    @pytest.mark.parametrize(
        "issue_count, expected_string",
        (
            (1, "numéro"),
            (2, "numéros"),
        ),
    )
    def test_pluralizarion_of_issue_count(self, issue_count, expected_string):
        journal = JournalFactory()
        IssueFactory.create_batch(journal=journal, size=issue_count)
        html = Client().get(journal_detail_url(journal)).content.decode()
        dom = BeautifulSoup(html, "html.parser")
        h2 = dom.find("section", {"id": "back-issues-section"}).find("h2")
        assert (
            h2.decode() == "<h2>\n        \n        "
            f"Historique de la revue ({issue_count}\xa0{expected_string})\n        \n      </h2>"
        )

    @pytest.mark.parametrize(
        "get_url, is_journal",
        (
            (journal_detail_url, True),
            (journal_authors_list_url, True),
            (issue_detail_url, False),
        ),
    )
    @override_settings(CACHES=settings.LOCMEM_CACHES)
    def test_journal_info_changes_refreshes_journal_base_html_template_cache(
        self, get_url, is_journal
    ):
        # Add publishing frequency information to journal information
        journal_info = JournalInformationFactory(frequency=1)
        issue = IssueFactory(journal=journal_info.journal)

        url = get_url(journal_info.journal if is_journal else issue)

        # Check if publishing frequency information is in html
        resp = Client().get(url)
        assert "1 numéro par année" in resp.content.decode()

        # Update publishing frequency information
        journal_info.frequency = 2
        journal_info.save()

        # Check if publishing frequency information was updated in html (refreshed cache)
        resp = Client().get(url)
        assert "2 numéros par année" in resp.content.decode()


class TestJournalAuthorsListView:
    def test_provides_only_authors_for_the_first_available_letter_by_default(self):
        issue_1 = IssueFactory.create(date_published=dt.datetime.now())
        ArticleFactory.create(issue=issue_1, authors=["btest", "ctest1", "ctest2"])

        url = reverse("public:journal:journal_authors_list", kwargs={"code": issue_1.journal.code})
        response = Client().get(url)

        assert response.status_code == 200
        assert set(response.context["authors_dicts"].keys()) == {
            "btest",
        }

    def test_only_provides_authors_for_the_given_letter(self):
        issue_1 = IssueFactory.create(date_published=dt.datetime.now())
        ArticleFactory.create(issue=issue_1, authors=["btest", "ctest1"])
        url = reverse("public:journal:journal_authors_list", kwargs={"code": issue_1.journal.code})
        response = Client().get(url, letter="b")

        assert response.status_code == 200
        authors_dicts = response.context["authors_dicts"]
        assert len(authors_dicts) == 1
        assert authors_dicts.keys() == {
            "btest",
        }

    def test_can_provide_contributors_of_article(self):
        issue_1 = IssueFactory.create(date_published=dt.datetime.now())
        ArticleFactory.create(issue=issue_1, authors=["btest", "ctest1"])
        url = reverse("public:journal:journal_authors_list", kwargs={"code": issue_1.journal.code})
        response = Client().get(url, letter="b")

        assert response.status_code == 200
        authors_dicts = response.context["authors_dicts"]
        contributors = authors_dicts["btest"][0]["contributors"]
        assert contributors == ["ctest1"]

    def test_dont_show_unpublished_articles(self):
        issue1 = IssueFactory.create(is_published=False)
        issue2 = IssueFactory.create(journal=issue1.journal, is_published=True)
        ArticleFactory.create(issue=issue1, authors=["foo"])
        ArticleFactory.create(issue=issue2, authors=["foo"])

        # Unpublished articles aren't in solr
        url = reverse("public:journal:journal_authors_list", kwargs={"code": issue1.journal.code})
        response = Client().get(url, letter="f")

        authors_dicts = response.context["authors_dicts"]
        # only one of the two articles are there
        assert len(authors_dicts["foo"]) == 1

    def test_can_filter_by_article_type(self):
        issue_1 = IssueFactory.create(date_published=dt.datetime.now())
        ArticleFactory.create(issue=issue_1, type="article", authors=["btest"])
        ArticleFactory.create(issue=issue_1, type="compterendu", authors=["btest"])

        url = reverse("public:journal:journal_authors_list", kwargs={"code": issue_1.journal.code})
        response = Client().get(url, article_type="article")
        assert response.status_code == 200
        authors_dicts = response.context["authors_dicts"]
        assert len(authors_dicts) == 1

    def test_can_filter_by_article_type_when_no_article_of_type(self):
        issue_1 = IssueFactory.create(date_published=dt.datetime.now())
        ArticleFactory.create(issue=issue_1, type="article", authors=["atest"])
        url = reverse("public:journal:journal_authors_list", kwargs={"code": issue_1.journal.code})
        response = Client().get(url, {"article_type": "compterendu"})

        assert response.status_code == 200

    def test_only_letters_with_results_are_active(self):
        """Test that for a given selection in the authors list view, only the letters for which
        results are present are shown"""
        issue_1 = IssueFactory.create(journal=JournalFactory(), date_published=dt.datetime.now())
        ArticleFactory.create(issue=issue_1, type="article", authors=["atest"])
        ArticleFactory.create(issue=issue_1, type="compterendu", authors=["btest"])
        url = reverse("public:journal:journal_authors_list", kwargs={"code": issue_1.journal.code})
        response = Client().get(url, {"article_type": "compterendu"})

        assert response.status_code == 200
        assert not response.context["letters_exists"].get("A")

    def test_do_not_fail_when_user_requests_a_letter_with_no_articles(self):
        issue_1 = IssueFactory.create(date_published=dt.datetime.now())
        ArticleFactory.create(issue=issue_1, type="article", authors=["btest"])

        url = reverse("public:journal:journal_authors_list", kwargs={"code": issue_1.journal.code})
        response = Client().get(url, {"article_type": "compterendu", "letter": "A"})

        assert response.status_code == 200

    def test_inserts_the_current_letter_in_the_context(self):
        issue_1 = IssueFactory.create(date_published=dt.datetime.now())
        ArticleFactory.create(issue=issue_1, authors=["btest", "ctest1", "ctest2"])

        url = reverse("public:journal:journal_authors_list", kwargs={"code": issue_1.journal.code})
        response_1 = Client().get(url)
        response_2 = Client().get(url, {"letter": "C"})
        response_3 = Client().get(url, {"letter": "invalid"})

        assert response_1.status_code == 200
        assert response_1.status_code == 200
        assert response_1.status_code == 200
        assert response_1.context["letter"] == "B"
        assert response_2.context["letter"] == "C"
        assert response_3.context["letter"] == "B"

    def test_inserts_a_dict_with_the_letters_counts_in_the_context(self):
        issue_1 = IssueFactory.create(date_published=dt.datetime.now())
        ArticleFactory.create(issue=issue_1, authors=["btest", "ctest1", "ctest2"])

        url = reverse("public:journal:journal_authors_list", kwargs={"code": issue_1.journal.code})
        response = Client().get(url)

        assert response.status_code == 200
        assert len(response.context["letters_exists"]) == 26
        assert response.context["letters_exists"]["B"]
        assert response.context["letters_exists"]["C"]
        for letter in "adefghijklmnopqrstuvwxyz":
            assert not response.context["letters_exists"][letter.upper()]

    @pytest.mark.parametrize("article_type,expected", [("compterendu", True), ("article", False)])
    def test_view_has_multiple_article_types(self, article_type, expected):
        article1 = ArticleFactory.create(type="article", authors=["btest"])
        ArticleFactory.create(issue=article1.issue, type=article_type, authors=["btest"])

        url = reverse(
            "public:journal:journal_authors_list", kwargs={"code": article1.issue.journal.code}
        )
        response = Client().get(url)

        assert response.context["view"].has_multiple_article_types == expected

    def test_no_duplicate_authors_with_lowercase_and_uppercase_names(self):
        issue = IssueFactory(journal__code="journal")
        ArticleFactory.create(issue=issue, localidentifier="article1", authors=["FOO, BAR"])
        ArticleFactory.create(issue=issue, localidentifier="article2", authors=["FOO, Bar"])
        ArticleFactory.create(issue=issue, localidentifier="article3", authors=["Foo, Bar"])

        url = reverse("public:journal:journal_authors_list", kwargs={"code": "journal"})
        response = Client().get(url)

        assert response.context["authors_dicts"] == OrderedDict(
            {
                "foo-bar": [
                    {
                        "author": "FOO, BAR",
                        "contributors": [],
                        "id": "article1",
                        "title": "Robert Southey, Writing and Romanticism",
                        "url": None,
                        "year": "2",
                    },
                    {
                        "author": "FOO, Bar",
                        "contributors": [],
                        "id": "article2",
                        "title": "Robert Southey, Writing and Romanticism",
                        "url": None,
                        "year": "2",
                    },
                    {
                        "author": "Foo, Bar",
                        "contributors": [],
                        "id": "article3",
                        "title": "Robert Southey, Writing and Romanticism",
                        "url": None,
                        "year": "2",
                    },
                ],
            }
        )


class TestIssueDetailView:
    def test_works_with_pks(self):
        issue = IssueFactory.create(date_published=dt.datetime.now())
        url = issue_detail_url(issue)
        response = Client().get(url)
        assert response.status_code == 200

    @pytest.mark.parametrize(
        "is_published,has_ticket,expected_code",
        [
            (True, False, 200),
            (True, True, 200),
            (False, False, 302),
            (False, True, 200),
        ],
    )
    def test_can_accept_prepublication_ticket(self, is_published, has_ticket, expected_code):
        localidentifier = "espace03368"
        issue = IssueFactory(localidentifier=localidentifier, is_published=is_published)
        url = issue_detail_url(issue)
        data = None
        if has_ticket:
            ticket = md5(localidentifier.encode()).hexdigest()
            data = {"ticket": ticket}
        response = Client().get(url, data=data)
        assert response.status_code == expected_code

    def test_works_with_localidentifiers(self):
        issue = IssueFactory.create(date_published=dt.datetime.now(), localidentifier="test")
        url = issue_detail_url(issue)
        response = Client().get(url)
        assert response.status_code == 200

    def test_fedora_issue_with_external_url_redirects(self):
        # When we have an issue with a fedora localidentifier *and* external_url set, we redirect
        # to that external url when we hit the detail view.
        # ref #1651
        issue = IssueFactory.create(
            date_published=dt.datetime.now(),
            localidentifier="test",
            external_url="http://example.com",
        )
        url = issue_detail_url(issue)
        response = Client().get(url)
        assert response.status_code == 302
        assert response.url == "http://example.com"

    def test_can_render_issue_summary_when_db_contains_articles_not_in_summary(self):
        # Articles in the issue view are ordered according to the list specified in the erudit
        # object. If an article isn't referenced in the erudit object list, then it will not be
        # shown. We rely on the fact that the default patched issue points to liberte1035607
        # ref support#216
        issue = IssueFactory.create()
        a1 = ArticleFactory.create(issue=issue, localidentifier="31492ac")
        a2 = ArticleFactory.create(issue=issue, localidentifier="31491ac")
        ArticleFactory.create(issue=issue, localidentifier="not-there", add_to_fedora_issue=False)
        url = issue_detail_url(issue)
        response = Client().get(url)
        articles = response.context["articles"]
        assert articles == [a1, a2]

    @pytest.mark.parametrize(
        "factory, expected_lock",
        [
            (EmbargoedIssueFactory, True),
            (OpenAccessIssueFactory, False),
        ],
    )
    def test_embargo_lock_icon(self, factory, expected_lock):
        issue = factory(is_published=False)
        url = issue_detail_url(issue)
        response = Client().get(url, {"ticket": issue.prepublication_ticket})
        # The embargo lock icon should never be displayed when a prepublication ticket is provided.
        assert b"ion-ios-lock" not in response.content
        issue.is_published = True
        issue.save()
        response = Client().get(url)
        # The embargo lock icon should only be displayed on embargoed issues.
        assert (b"ion-ios-lock" in response.content) == expected_lock

    @override_settings(CACHES=settings.LOCMEM_CACHES)
    @unittest.mock.patch("eruditarticle.objects.publication.EruditPublication.get_summary_articles")
    @pytest.mark.parametrize("is_published", (True, False))
    def test_article_items_are_cached_for_published_and_unpublished_issues(
        self, mock_get_summary_articles, is_published, monkeypatch
    ):
        """Tests that articles on published or unpublished issue detail pages are cached.

        Whether an issue is published or not, the articles displayed on the issue detail page
        should always be cached.
        """
        # Create a published or unpublished issue.
        issue = IssueFactory(is_published=is_published)

        # Mock a SummaryArticle with a title to test for.
        article = SummaryArticle(
            localidentifier="article1",
            processing="complet",
            html_title="thisismyoldtitle",
        )
        mock_get_summary_articles.return_value = [article]

        # Send a request for the issue detail page so that the article is cached.
        url = issue_detail_url(issue)
        resp = Client().get(url, {"ticket": issue.prepublication_ticket})

        # Check that the expected article title is displayed.
        assert "thisismyoldtitle" in resp.content.decode()

        # Set a new article title.
        article.html_title = "thisismynewtitle"
        mock_get_summary_articles.return_value = [article]

        # The old title should be displayed since it was cached.
        resp = Client().get(url, {"ticket": issue.prepublication_ticket})
        assert "thisismyoldtitle" in resp.content.decode()

        # With the cache cleared, the new title should be displayed.
        cache.clear()
        resp = Client().get(url, {"ticket": issue.prepublication_ticket})
        assert "thisismynewtitle" in resp.content.decode()

    def test_can_return_404_when_issue_doesnt_exist(self):
        issue = IssueFactory(
            localidentifier="test",
        )
        issue.localidentifier = "fail"
        url = issue_detail_url(issue)
        response = Client().get(url)
        assert response.status_code == 404

    @pytest.mark.parametrize("publication_allowed", (True, False))
    def test_publication_allowed_article(self, publication_allowed):
        issue = IssueFactory(journal__open_access=True)
        ArticleFactory(issue=issue, publication_allowed=publication_allowed)
        url = reverse(
            "public:journal:issue_detail",
            kwargs={
                "journal_code": issue.journal.code,
                "issue_slug": issue.volume_slug,
                "localidentifier": issue.localidentifier,
            },
        )
        html = Client().get(url).content.decode()
        dom = BeautifulSoup(html, "html.parser")
        toolbox = dom.find("ul", {"class": "toolbox"})
        summary_link = dom.find("p", {"class": "bib-record__record-link"})
        if publication_allowed:
            assert toolbox
            assert summary_link
        else:
            assert not toolbox
            assert not summary_link

    @override_settings(CACHES=settings.LOCMEM_CACHES)
    @unittest.mock.patch("eruditarticle.objects.publication.EruditPublication.get_summary_articles")
    @pytest.mark.parametrize(
        "language_code, expected_link",
        (
            (
                "fr",
                '<a class="tool-btn" href="/fr/revues/journal/2000-issue/article.pdf" '
                'target="_blank" title="Télécharger">',
            ),
            (
                "en",
                '<a class="tool-btn" href="/en/journals/journal/2000-issue/article.pdf" '
                'target="_blank" title="Download">',
            ),
        ),
    )
    def test_article_pdf_url_is_cache_with_the_right_language(
        self,
        mock_get_summary_articles,
        language_code,
        expected_link,
    ):
        issue = IssueFactory(
            journal__code="journal",
            year="2000",
            localidentifier="issue",
        )
        mock_get_summary_articles.return_value = [
            SummaryArticle(
                localidentifier="article",
                processing="complet",
                urlpdf="/url.pdf",
            ),
        ]
        with override_settings(LANGUAGE_CODE=language_code):
            url = reverse(
                "public:journal:issue_detail",
                kwargs={
                    "journal_code": issue.journal.code,
                    "issue_slug": issue.volume_slug,
                    "localidentifier": issue.localidentifier,
                },
            )
            html = Client().get(url).content.decode()
            dom = BeautifulSoup(html, "html.parser")
            toolbox = dom.find("ul", {"class": "toolbox"})
            assert expected_link in toolbox.decode()

    def test_journal_titles_and_subtitles_are_displayed_in_all_languages(self):
        issue = IssueFactory(journal__code="journal")
        repository.api.set_publication_xml(
            issue.get_full_identifier(),
            open("tests/fixtures/issue/im03868.xml", "rb").read(),
        )
        url = reverse(
            "public:journal:issue_detail",
            kwargs={
                "journal_code": issue.journal.code,
                "issue_slug": issue.volume_slug,
                "localidentifier": issue.localidentifier,
            },
        )
        html = Client().get(url).content.decode()
        # Use lxml parser to avoid closing </br> tags being added to the html.
        dom = BeautifulSoup(html, "lxml")
        title1 = dom.find("p", {"class": "main-header__meta"}).decode()
        assert (
            title1 == '<p class="main-header__meta">\n'
            '<a href="/fr/revues/journal/" title="Consulter la revue">\n        '
            "Intermédialités\n        \n        \n        "
            '<span class="hint--bottom-left hint--no-animate" '
            'data-hint="Tous les articles de cette revue sont soumis à un processus '
            'd’évaluation par les pairs.">\n'
            '<i class="icon ion-ios-checkmark-circle"></i>\n'
            "</span>\n<br/>\n"
            '<span class="journal-subtitle">Histoire et théorie des arts, '
            "des lettres et des techniques</span>\n<br/>\n          "
            "Intermediality\n          \n          \n          <br/>\n"
            '<span class="journal-subtitle">History and Theory of the Arts, '
            "Literature and Technologies</span>\n</a>\n</p>"
        )

        title2 = dom.find("div", {"class": "latest-issue"}).find("h2").decode()
        assert (
            title2 == '<h2>\n<a href="/fr/revues/journal/" title="Consulter la revue">\n      '
            "Intermédialités\n      \n      <br/>\n"
            '<span class="journal-subtitle">Histoire et théorie des arts, '
            "des lettres et des techniques</span>\n<br/>\n        "
            "Intermediality\n        \n        \n        <br/>\n"
            '<span class="journal-subtitle">History and Theory of the Arts, '
            "Literature and Technologies</span>\n</a>\n</h2>"
        )

    @pytest.mark.parametrize(
        "collection_code, expected_document_id",
        (
            ("erudit", "article1"),
            ("unb", "unb:article1"),
        ),
    )
    def test_data_document_id_includes_unb_prefix(self, collection_code, expected_document_id):
        article = ArticleFactory(
            issue__journal__collection__code=collection_code,
            localidentifier="article1",
        )
        url = reverse(
            "public:journal:issue_detail",
            kwargs={
                "journal_code": article.issue.journal.code,
                "issue_slug": article.issue.volume_slug,
                "localidentifier": article.issue.localidentifier,
            },
        )
        html = Client().get(url).content.decode()
        assert f'data-document-id="{expected_document_id}"' in html

    @pytest.mark.parametrize("issue_xml", ("ritpu0326.xml", "ritpu1824085.xml"))
    def test_absence_of_copyright_and_presence_of_license_image_in_issue_summary(self, issue_xml):
        issue = IssueFactory(journal__code="journal")
        repository.api.set_publication_xml(
            issue.get_full_identifier(),
            open(f"tests/fixtures/issue/{issue_xml}", "rb").read(),
        )
        url = reverse(
            "public:journal:issue_detail",
            kwargs={
                "journal_code": issue.journal.code,
                "issue_slug": issue.volume_slug,
                "localidentifier": issue.localidentifier,
            },
        )
        html = Client().get(url).content.decode()
        assert "<p><small>Tous droits réservés © CRÉPUQ, 2012</small></p>" not in html
        assert (
            '<p><a href="http://creativecommons.org/licenses/by-nc-sa/'
            '3.0/deed.fr_CA" target="_blank">' in html
        )

    @pytest.mark.parametrize(
        "article_count, expected_string",
        (
            (1, "article"),
            (2, "articles"),
        ),
    )
    def test_pluralizarion_of_article_count(self, article_count, expected_string):
        issue = IssueFactory()
        ArticleFactory.create_batch(issue=issue, size=article_count)
        html = Client().get(issue_detail_url(issue)).content.decode()
        dom = BeautifulSoup(html, "html.parser")
        h2 = dom.find("header", {"class": "main-header"}).find("h2")
        assert (
            h2.decode() == '<h2 class="toc__title">\n      \n      '
            f"Sommaire ({article_count}\xa0{expected_string})\n      \n    </h2>"
        )

    @unittest.mock.patch("eruditarticle.objects.publication.EruditPublication.get_summary_articles")
    def test_link_to_external_url_for_articles_belonging_to_external_issues(
        self, mock_get_summary_articles
    ):
        issue = IssueFactory()
        # Mock a SummaryArticle with a title to test for.
        article = SummaryArticle(
            localidentifier="article",
            processing="complet",
            urlhtml="https://test/",
        )
        mock_get_summary_articles.return_value = [article]
        html = Client().get(issue_detail_url(issue)).content.decode()
        dom = BeautifulSoup(html, "html.parser")
        a = dom.find("h6", {"class": "bib-record__title"}).find("a")
        assert (
            a.decode() == '<a href="https://test/" target="_blank" title="Lire l\'article">'
            "\n    None\n    </a>"
        )


class TestArticleDetailView:
    @pytest.fixture(autouse=True)
    def article_detail_solr_data(self, monkeypatch):
        monkeypatch.setattr(SolrDataMixin, "solr_data", FakeSolrData())

    @pytest.mark.parametrize("method", ["get", "options"])
    def test_can_render_erudit_articles(self, monkeypatch, eruditarticle, method):
        # The goal of this test is to verify that out erudit article mechanism doesn't crash for
        # all kinds of articles. We have many articles in our fixtures and the `eruditarticle`
        # argument here is a parametrization argument which causes this test to run for each
        # fixture we have.
        monkeypatch.setattr(metrics_settings, "ACTIVATED", False)
        monkeypatch.setattr(Article, "get_erudit_object", lambda *a, **kw: eruditarticle)
        journal = JournalFactory.create(open_access=True)
        issue = IssueFactory.create(
            journal=journal, date_published=dt.datetime.now(), localidentifier="test_issue"
        )
        article = ArticleFactory.create(issue=issue, localidentifier="test_article")
        url = article_detail_url(article)
        response = getattr(Client(), method)(url)
        assert response.status_code == 200

    @pytest.mark.parametrize(
        "is_published,has_ticket,expected_code",
        [
            (True, False, 200),
            (True, True, 200),
            (False, False, 302),
            (False, True, 200),
        ],
    )
    def test_can_accept_prepublication_ticket(self, is_published, has_ticket, expected_code):
        localidentifier = "espace03368"
        issue = IssueFactory(localidentifier=localidentifier, is_published=is_published)
        article = ArticleFactory(issue=issue)
        url = article_detail_url(article)
        data = None
        if has_ticket:
            ticket = md5(localidentifier.encode()).hexdigest()
            data = {"ticket": ticket}
        response = Client().get(url, data=data)
        assert response.status_code == expected_code

    @pytest.mark.parametrize(
        "is_published,ticket_expected",
        [
            (True, False),
            (False, True),
        ],
    )
    def test_prepublication_ticket_is_propagated_to_other_pages(
        self, is_published, ticket_expected
    ):
        localidentifier = "espace03368"
        issue = IssueFactory(localidentifier=localidentifier, is_published=is_published)
        articles = ArticleFactory.create_batch(issue=issue, size=3)
        article = articles[1]
        url = article_detail_url(article)
        ticket = md5(localidentifier.encode()).hexdigest()
        response = Client().get(url, data={"ticket": ticket})

        from io import StringIO

        tree = et.parse(StringIO(response.content.decode()), et.HTMLParser())

        # Test that the ticket is in the breadcrumbs
        bc_hrefs = [e.get("href") for e in tree.findall('.//nav[@id="breadcrumbs"]//a')]
        pa_hrefs = [e.get("href") for e in tree.findall('.//div[@class="pagination-arrows"]/a')]

        # This is easier to debug than a generator
        for href in bc_hrefs + pa_hrefs:
            assert ("ticket" in href) == ticket_expected

    def test_dont_cache_html_of_articles_of_unpublished_issues(self):
        issue = IssueFactory.create(is_published=False)
        article = ArticleFactory.create(issue=issue, title="thiswillendupinhtml")
        url = "{}?ticket={}".format(article_detail_url(article), issue.prepublication_ticket)
        response = Client().get(url)
        assert response.status_code == 200
        assert b"thiswillendupinhtml" in response.content

        with repository.api.open_article(article.pid) as wrapper:
            wrapper.set_title("thiswillreplaceoldinhtml")
        response = Client().get(url)
        assert response.status_code == 200
        assert b"thiswillendupinhtml" not in response.content
        assert b"thiswillreplaceoldinhtml" in response.content

    def test_cache_fedora_objects_of_articles_of_unpublished_issues(self):

        issue = IssueFactory.create(is_published=False)
        article = ArticleFactory.create(issue=issue)
        with unittest.mock.patch("erudit.fedora.cache.cache") as cache_mock:
            cache_mock.get.return_value = None
            url = "{}?ticket={}".format(article_detail_url(article), issue.prepublication_ticket)
            response = Client().get(url)
            assert response.status_code == 200
            # Assert that the cache has not be called.
            assert cache_mock.get.call_count == 4

    def test_allow_ephemeral_articles(self):
        # When receiving a request for an article that doesn't exist in the DB, try querying fedora
        # for the requested PID before declaring a failure.
        issue = IssueFactory.create()
        article_localidentifier = "foo"
        repository.api.register_article(
            "{}.{}".format(issue.get_full_identifier(), article_localidentifier)
        )

        Article = namedtuple("Article", "localidentifier html_title issue pid")
        repository.api.add_article_to_parent_publication(
            Article(localidentifier="foo", html_title="bar", issue=issue, pid="foo")
        )
        url = reverse(
            "public:journal:article_detail",
            kwargs={
                "journal_code": issue.journal.code,
                "issue_slug": issue.volume_slug,
                "issue_localid": issue.localidentifier,
                "localid": article_localidentifier,
            },
        )
        response = Client().get(url)
        assert response.status_code == 200

    @unittest.mock.patch("fitz.Document")
    @unittest.mock.patch("eulfedora.models.FileDatastreamObject._get_content")
    @pytest.mark.parametrize(
        "content_access_granted,has_abstracts,should_fetch_pdf",
        ((True, True, False), (True, False, False), (False, True, False), (False, False, True)),
    )
    def test_do_not_fetch_pdfs_if_not_necessary(
        self, mock_fitz, mock_content, content_access_granted, has_abstracts, should_fetch_pdf
    ):
        """Test that the PDF is only fetched on ArticleDetailView when the the user is not subscribed
        and the article has no abstract
        """
        article = ArticleFactory(with_pdf=True)
        client = Client()

        if has_abstracts:
            with repository.api.open_article(article.pid) as wrapper:
                wrapper.set_abstracts([{"lang": "fr", "content": "Résumé français"}])
        if content_access_granted:
            subscription = JournalAccessSubscriptionFactory(
                pk=1,
                user__password="password",
                post__valid=True,
                post__journals=[article.issue.journal],
                organisation=None,  # TODO implement IndividualJournalAccessSubscriptionFactory
            )
            client.login(username=subscription.user.username, password="password")

        url = article_detail_url(article)
        response = client.get(url)
        if should_fetch_pdf:
            assert mock_content.call_count == 1
        else:
            assert mock_content.call_count == 0
        assert response.status_code == 200

    def test_querystring_doesnt_mess_media_urls(self):
        journal = JournalFactory(open_access=True)  # so we see the whole article
        issue = IssueFactory(journal=journal)
        article = ArticleFactory(issue=issue, from_fixture="1003446ar")  # this article has media
        url = "{}?foo=bar".format(article_detail_url(article))
        response = Client().get(url)
        # we have some media urls
        assert b"media/" in response.content
        # We don't have any messed up media urls, that is, an URL with our querystring in the
        # middle
        assert b"barmedia/" not in response.content

    @unittest.mock.patch("erudit.fedora.cache.cache")
    @unittest.mock.patch("erudit.fedora.cache.get_cached_datastream_content")
    def test_pdf_datastream_caching(self, mock_get_cached_datastream_content, mock_cache):
        mock_cache.get.return_value = None
        mock_get_cached_datastream_content.return_value = None
        article = ArticleFactory(
            issue__journal__open_access=True,
        )
        url = reverse(
            "public:journal:article_raw_pdf",
            kwargs={
                "journal_code": article.issue.journal.code,
                "issue_slug": article.issue.volume_slug,
                "issue_localid": article.issue.localidentifier,
                "localid": article.localidentifier,
            },
        )
        mock_cache.get.reset_mock()

        Client().get(url)
        assert mock_cache.get.call_count == 3

    @unittest.mock.patch("erudit.fedora.cache.cache")
    @pytest.mark.parametrize(
        "is_published, expected_count",
        [
            (False, 3),
            (True, 3),
        ],
    )
    def test_xml_datastream_caching(self, mock_cache, is_published, expected_count):
        mock_cache.get.return_value = None

        article = ArticleFactory(
            issue__is_published=is_published,
            issue__journal__open_access=True,
        )
        url = reverse(
            "public:journal:article_raw_xml",
            kwargs={
                "journal_code": article.issue.journal.code,
                "issue_slug": article.issue.volume_slug,
                "issue_localid": article.issue.localidentifier,
                "localid": article.localidentifier,
            },
        )
        mock_cache.get.reset_mock()

        Client().get(
            url,
            {
                "ticket": article.issue.prepublication_ticket,
            },
        )
        assert mock_cache.get.call_count == expected_count

    def test_that_article_titles_are_truncated_in_breadcrumb(self):
        article = ArticleFactory(
            from_fixture="1056823ar",
            localidentifier="article",
            issue__localidentifier="issue",
            issue__year="2000",
            issue__journal__code="journal",
        )
        url = article_detail_url(article)
        response = Client().get(url)
        html = response.content.decode()
        assert (
            '<a href="/fr/revues/journal/2000-issue/article/">Jean-Guy Desjardins, Traité de '
            "l’évaluation foncière, Montréal, Wilson &amp; Lafleur …</a>" in html
        )

    def test_keywords_html_tags(self):
        article = ArticleFactory(from_fixture="1055883ar")
        url = article_detail_url(article)
        response = Client().get(url)
        html = response.content.decode()
        # Check that HTML tags are displayed in the body.
        assert (
            '<ul>\n<li class="keyword">Charles Baudelaire, </li>\n<li class="keyword">\n'
            '<em>Fleurs du Mal</em>, </li>\n<li class="keyword">Seine, </li>\n'
            '<li class="keyword">mythe et réalité de Paris, </li>\n'
            '<li class="keyword">poétique du miroir</li>\n</ul>' in html
        )
        # Check that HTML tags are not displayed in the head.
        assert (
            '<meta name="citation_keywords" lang="fr" content="Charles Baudelaire, Fleurs du '
            'Mal, Seine, mythe et réalité de Paris, poétique du miroir" />' in html
        )

    def test_article_pdf_links(self):
        article = ArticleFactory(
            with_pdf=True,
            from_fixture="602354ar",
            localidentifier="602354ar",
            issue__year="2000",
            issue__localidentifier="issue",
            issue__is_published=False,
            issue__journal__code="journal",
            issue__journal__open_access=True,
        )
        url = article_detail_url(article)
        response = Client().get(
            url,
            {
                "ticket": article.issue.prepublication_ticket
                if not article.issue.is_published
                else "",
            },
        )
        html = response.content.decode()

        # Check that the PDF download button URL has the prepublication ticket if the issue is not
        # published.
        assert (
            '<a class="tool-btn tool-download" '
            'data-href="/fr/revues/journal/2000-issue/602354ar.pdf?'
            'ticket=0aae4c8f3cc35693d0cbbe631f2e8b52"><span class="toolbox-pdf">PDF</span>'
            '<span class="tools-label">Télécharger</span></a>' in html
        )
        # Check that the PDF menu link URL has the prepublication ticket if the issue is not
        # published.
        assert (
            '<a href="#pdf-viewer" id="pdf-viewer-menu-link">Texte intégral (PDF)</a>'
            '<a href="/fr/revues/journal/2000-issue/602354ar.pdf?'
            'ticket=0aae4c8f3cc35693d0cbbe631f2e8b52" id="pdf-download-menu-link" '
            'target="_blank">Texte intégral (PDF)</a>' in html
        )
        # Check that the embeded PDF URL has the prepublication ticket if the issue is not
        # published.
        assert (
            '<object id="pdf-viewer" data="/fr/revues/journal/2000-issue/602354ar.pdf?'
            'embed&amp;ds_name=PDF&amp;ticket=0aae4c8f3cc35693d0cbbe631f2e8b52" '
            'type="application/pdf" style="width: 100%; height: 700px;"></object>' in html
        )
        # Check that the PDF download link URL has the prepublication ticket if the issue is not
        # published.
        assert (
            '<a href="/fr/revues/journal/2000-issue/602354ar.pdf?'
            'ticket=0aae4c8f3cc35693d0cbbe631f2e8b52" class="btn btn-secondary" '
            'target="_blank">Télécharger</a>' in html
        )

        article.issue.is_published = True
        article.issue.save()
        response = Client().get(url)
        html = response.content.decode()

        # Check that the PDF download button URL does not have the prepublication ticket if the
        # issue is published.
        assert (
            '<a class="tool-btn tool-download" data-href="/fr/revues/journal/2000-issue/'
            '602354ar.pdf"><span class="toolbox-pdf">PDF</span><span '
            'class="tools-label">Télécharger</span></a>' in html
        )
        # Check that the PDF menu link URL does not have the prepublication ticket if the issue
        # is published.
        assert (
            '<a href="#pdf-viewer" id="pdf-viewer-menu-link">Texte intégral (PDF)</a>'
            '<a href="/fr/revues/journal/2000-issue/602354ar.pdf" id="pdf-download-menu-link" '
            'target="_blank">Texte intégral (PDF)</a>' in html
        )
        # Check that the embeded PDF URL does not have the prepublication ticket if the issue is
        # published.
        assert (
            '<object id="pdf-viewer" data="/fr/revues/journal/2000-issue/602354ar.pdf?embed&amp;'
            'ds_name=PDF" type="application/pdf" style="width: 100%; height: 700px;"></object>'
            in html
        )
        # Check that the PDF download link URL does not have the prepublication ticket if the issue
        # is published.
        assert (
            '<a href="/fr/revues/journal/2000-issue/602354ar.pdf" class="btn btn-secondary" '
            'target="_blank">Télécharger</a>' in html
        )

    @pytest.mark.parametrize(
        "kwargs, nonce_count, authorized",
        (
            # Valid token
            ({}, 1, True),
            # Badly formed token
            ({"token_separator": "!"}, 1, False),
            # Invalid nonce
            ({"invalid_nonce": True}, 1, False),
            # Invalid message
            ({"invalid_message": True}, 1, False),
            # Invalid signature
            ({"invalid_signature": True}, 1, False),
            # Nonce seen more than 3 times
            ({}, 4, False),
            # Badly formatted payload
            ({"payload_separator": "!"}, 1, False),
            # Expired token
            ({"time_delta": 3600000001}, 1, False),
            # Wrong IP
            ({"ip_subnet": "8.8.8.0/24"}, 1, False),
            # Invalid subscription
            ({"subscription_id": 2}, 1, False),
        ),
    )
    @pytest.mark.parametrize(
        "url_name",
        (
            ("public:journal:article_detail"),
            ("public:journal:article_raw_pdf"),
        ),
    )
    @unittest.mock.patch("core.subscription.middleware.SubscriptionMiddleware._nonce_count")
    @override_settings(GOOGLE_CASA_KEY="74796E8FF6363EFF91A9308D1D05335E")
    def test_article_detail_with_google_casa_token(
        self, mock_nonce_count, url_name, kwargs, nonce_count, authorized
    ):
        mock_nonce_count.return_value = nonce_count
        article = ArticleFactory()
        JournalAccessSubscriptionFactory(
            pk=1,
            post__valid=True,
            post__journals=[article.issue.journal],
        )
        url = reverse(
            url_name,
            kwargs={
                "journal_code": article.issue.journal.code,
                "issue_slug": article.issue.volume_slug,
                "issue_localid": article.issue.localidentifier,
                "localid": article.localidentifier,
            },
        )
        response = Client().get(
            url,
            {
                "casa_token": generate_casa_token(**kwargs),
            },
            follow=True,
        )
        html = response.content.decode()
        if authorized:
            assert "Seuls les 600 premiers mots du texte seront affichés." not in html
        else:
            assert "Seuls les 600 premiers mots du texte seront affichés." in html

    @pytest.mark.parametrize(
        "url_name, fixture, display_biblio, display_pdf_first_page",
        (
            # Complete treatment articles should always display a bibliography
            ("public:journal:article_biblio", "009256ar", 1, 0),
            ("public:journal:article_summary", "009256ar", 1, 0),
            ("public:journal:article_detail", "009256ar", 1, 0),
            # Retro minimal treatment articles should only display a bibliography in article_biblio
            # view
            ("public:journal:article_biblio", "1058447ar", 1, 0),
            ("public:journal:article_summary", "1058447ar", 0, 1),
            ("public:journal:article_detail", "1058447ar", 0, 1),
            # Bibliography should not be displayed on TOC page.
            ("public:journal:article_toc", "009256ar", 0, 0),
            ("public:journal:article_toc", "1058447ar", 0, 0),
        ),
    )
    def test_biblio_references_display(
        self, url_name, fixture, display_biblio, display_pdf_first_page
    ):
        article = ArticleFactory(
            from_fixture=fixture,
            with_pdf=True,
        )
        url = reverse(
            url_name,
            kwargs={
                "journal_code": article.issue.journal.code,
                "issue_slug": article.issue.volume_slug,
                "issue_localid": article.issue.localidentifier,
                "localid": article.localidentifier,
            },
        )
        html = Client().get(url).content.decode()
        assert (
            html.count(
                '<section id="grbiblio" class="article-section grbiblio" ' 'role="complementary">'
            )
            == display_biblio
        )
        # Minimal treatment articles should not display PDF first page when displaying references.
        assert html.count('<object id="pdf-viewer"') == display_pdf_first_page

    @pytest.mark.parametrize("open_access", (True, False))
    @pytest.mark.parametrize(
        "url_name",
        (
            ("public:journal:article_biblio"),
            ("public:journal:article_summary"),
            ("public:journal:article_detail"),
            ("public:journal:article_toc"),
        ),
    )
    def test_display_citation_fulltext_world_readable_metatag_only_for_open_access_articles(
        self, url_name, open_access
    ):
        article = ArticleFactory(issue__journal__open_access=open_access)
        url = reverse(
            url_name,
            kwargs={
                "journal_code": article.issue.journal.code,
                "issue_slug": article.issue.volume_slug,
                "issue_localid": article.issue.localidentifier,
                "localid": article.localidentifier,
            },
        )
        html = Client().get(url).content.decode()
        # The citation_fulltext_world_readable metatag should only be displayed for open access
        # articles. Otherwise, some Google Scholar services won't work (eg. CASA).
        if open_access:
            assert '<meta name="citation_fulltext_world_readable" content="" />' in html
        else:
            assert '<meta name="citation_fulltext_world_readable" content="" />' not in html

    @pytest.mark.parametrize("publication_allowed", (True, False))
    @pytest.mark.parametrize(
        "url_name",
        (
            ("public:journal:article_biblio"),
            ("public:journal:article_summary"),
            ("public:journal:article_detail"),
            ("public:journal:article_toc"),
        ),
    )
    def test_publication_allowed_text_display(self, url_name, publication_allowed):
        article = ArticleFactory(
            publication_allowed=publication_allowed,
            issue__journal__open_access=True,
        )
        url = reverse(
            url_name,
            kwargs={
                "journal_code": article.issue.journal.code,
                "issue_slug": article.issue.volume_slug,
                "issue_localid": article.issue.localidentifier,
                "localid": article.localidentifier,
            },
        )
        html = Client().get(url).content.decode()
        dom = BeautifulSoup(html, "html.parser")
        if publication_allowed:
            assert "Plan de l’article" in dom.decode()
            assert "Boîte à outils" in dom.decode()
            if url_name != "public:journal:article_detail":
                assert "Lire le texte intégral" in dom.decode()
            if url_name not in ["public:journal:article_biblio", "public:journal:article_toc"]:
                assert (
                    "In October 1800 the poet, travel-writer and polemicist Robert Southey "
                    "was in Portugal." in dom.decode()
                )
        else:
            assert "Plan de l’article" not in dom.decode()
            assert "Boîte à outils" not in dom.decode()
            assert "Lire le texte intégral" not in dom.decode()
            assert (
                "In October 1800 the poet, travel-writer and polemicist Robert Southey was in "
                "Portugal." not in dom.decode()
            )

    def test_article_detail_marquage_in_toc_nav(self):
        issue = IssueFactory(
            journal__code="journal",
            localidentifier="issue",
            year="2000",
        )
        ArticleFactory(
            from_fixture="1054008ar",
            localidentifier="prev_article",
            issue=issue,
        )
        article = ArticleFactory(
            issue=issue,
        )
        ArticleFactory(
            from_fixture="1054008ar",
            localidentifier="next_article",
            issue=issue,
        )
        url = article_detail_url(article)
        response = Client().get(url)
        html = response.content.decode()

        tree = et.parse(io.StringIO(html), et.HTMLParser())

        h4s = tree.findall('.//h4[@class="toc-nav__title"]')
        for h4 in h4s:
            assert h4.text.strip() == "L’action et le verbe dans <em>Feuillets d’Hypnos</em>"

    def test_surtitre_not_split_in_multiple_spans(self):
        article = ArticleFactory(
            from_fixture="1056389ar",
        )
        url = article_detail_url(article)
        response = Client().get(url)
        html = response.content.decode()
        assert (
            '<span class="surtitre">Cahier commémoratif : '
            "25<sup>e</sup> anniversaire</span>" in html
        )

    def test_title_and_paral_title_are_displayed(self):
        article = ArticleFactory(
            from_fixture="1058368ar",
        )
        url = article_detail_url(article)
        response = Client().get(url)
        html = response.content.decode()
        assert (
            '<span class="titre">Les Parcs Nationaux de Roumanie : considérations sur les '
            "habitats Natura 2000 et sur les réserves IUCN</span>" in html
        )
        assert (
            '<span class="titreparal">The National Parks of Romania: considerations on Natura '
            "2000 habitats and IUCN reserves</span>" in html
        )

    def test_article_detail_view_with_untitled_article(self):
        article = ArticleFactory(
            from_fixture="1042058ar",
            localidentifier="article",
            issue__year="2000",
            issue__localidentifier="issue",
            issue__journal__code="journal",
            issue__journal__name="Revue",
        )
        url = article_detail_url(article)
        html = Client().get(url).content.decode()
        # Check that "[Article sans titre]" is displayed in the header title.
        assert "<title>[Article sans titre] – Inter – Érudit</title>" in html
        # Check that "[Article sans titre]" is displayed in the body title.
        assert (
            '<h1 class="doc-head__title"><span class="titre">[Article sans titre]</span></h1>'
            in html
        )
        # Check that "[Article sans titre]" is displayed in the breadcrumbs.
        assert (
            '<li>\n  <a href="/fr/revues/journal/2000-issue/article/">[Article sans titre]</a>'
            "\n</li>" in html
        )

    def test_article_authors_with_suffixes(self):
        article = ArticleFactory(
            from_fixture="1058611ar",
        )
        url = article_detail_url(article)
        html = Client().get(url).content.decode()
        # Check that authors' suffixes are not displayed on the the author list under the article
        # title.
        assert (
            '<li class="auteur doc-head__author">\n<span class="nompers">André\n      '
            "Ngamini-Ngui</span> et </li>" in html
        )
        # Check that authors' suffixes are displayed on the 'more information' section.
        assert (
            '<li class="auteur-affiliation"><p><strong>André\n      Ngamini-Ngui, †</strong>'
            "</p></li>" in html
        )

    def test_figure_groups_source_display(self):
        article = ArticleFactory(
            from_fixture="1058470ar",
            localidentifier="article",
            issue__year="2000",
            issue__localidentifier="issue",
            issue__journal__code="journal",
            issue__journal__open_access=True,
        )
        url = article_detail_url(article)
        html = Client().get(url).content.decode()
        dom = BeautifulSoup(html, "html.parser")
        grfigure = dom.find("div", {"class": "grfigure", "id": "gf1"})

        # Check that the source is displayed under both figures 1 & 2 which are in the same figure
        # group.
        fi1 = grfigure.find("figure", {"id": "fi1"}).decode()
        fi2 = grfigure.find("figure", {"id": "fi2"}).decode()
        assert (
            fi1 == '<figure class="figure" id="fi1"><figcaption></figcaption><div '
            'class="figure-wrapper">\n<div class="figure-object"><a class="lightbox '
            'objetmedia" href="/fr/revues/journal/2000-issue/article/media/" title="">'
            '<img alt="" class="lazyload img-responsive" data-aspectratio="/" '
            'data-srcset="/fr/revues/journal/2000-issue/article/media/ w" height="" '
            'src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAA'
            'AC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=" width=""/></a></div>\n'
            '<div class="figure-legende-notes-source"><cite class="source">Avec '
            "l’aimable autorisation de l’artiste et kamel mennour, Paris/London. © "
            "<em>ADAGP Mohamed Bourouissa</em></cite></div>\n</div></figure>"
        )
        assert (
            fi2 == '<figure class="figure" id="fi2"><figcaption></figcaption><div '
            'class="figure-wrapper">\n<div class="figure-object"><a class="lightbox '
            'objetmedia" href="/fr/revues/journal/2000-issue/article/media/" title="">'
            '<img alt="" class="lazyload img-responsive" data-aspectratio="/" '
            'data-srcset="/fr/revues/journal/2000-issue/article/media/ w" height="" '
            'src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAA'
            'AC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=" width=""/></a></div>\n'
            '<div class="figure-legende-notes-source"><cite class="source">Avec '
            "l’aimable autorisation de l’artiste et kamel mennour, Paris/London. © "
            "<em>ADAGP Mohamed Bourouissa</em></cite></div>\n</div></figure>"
        )

        # Check that the figure list link is displayed.
        voirliste = grfigure.find("p", {"class": "voirliste"})
        assert (
            voirliste.decode() == '<p class="voirliste"><a href="#ligf1">-&gt; Voir la liste '
            "des figures</a></p>"
        )

    def test_equation_caption_position(self):
        article = ArticleFactory(
            from_fixture="1077786ar",
            localidentifier="article",
            issue__year="2021",
            issue__localidentifier="issue",
            issue__journal__code="journal",
            issue__journal__open_access=True,
        )
        url = article_detail_url(article)
        response = Client().get(url)
        html = response.content.decode()
        # Check that the type `titre` captions are displayed above the equation and that the
        # type `alinea` are displayed bellow
        assert (
            '<aside class="equation">'
            '<div class="legende"><p class="legende"><strong class="titre">'
            "Equation 5 : Profitability measurement</strong></p></div>\n"
            '<span class="no">(5)</span><img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA'
            'EAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=" data-srcset="/fr/'
            'revues/journal/2021-issue/article/media/2181034.jpg 91w" data-aspectratio="2.06818181'
            '8181818" width="91" height="44" class="lazyload" id="im5" alt="equation: equation ple'
            'ine grandeur">'
            '<div class="legende">\n<p class="alinea">With:</p>\n'
            '<p class="alinea"><em>S</em><sub><em>i</em></sub> <em>= Sharpe\n'
            "              Ratio</em></p>\n"
            '<p class="alinea"><em>R</em><sub><em>i</em></sub> <em>= return of the asset\n'
            "              </em></p>\n"
            '<p class="alinea"><em>R</em><sub><em>f</em></sub> <em>= risk-free\n'
            "              rate</em></p>\n"
            '<p class="alinea">σ<sub><em>i</em></sub> <em>= Strandard deviation of the asset’s'
            " excess return\n              5</em></p>\n</div></aside>" in html
        )

    def test_figure_with_float_dimensions(self, monkeypatch):
        article = ArticleFactory(
            from_fixture="1068859ar",
            localidentifier="article",
            issue__year="2000",
            issue__localidentifier="issue",
            issue__journal__code="journal",
            issue__journal__open_access=True,
        )

        import erudit.models.journal

        monkeypatch.setattr(
            erudit.models.journal,
            "get_cached_datastream_content",
            unittest.mock.MagicMock(
                return_value=b"""
<infoDoc>
    <im id="img-05-01.png">
        <imPlGr>
            <nomImg>2135184.png</nomImg>
            <dimx>863.0</dimx>
            <dimy>504.0</dimy>
            <taille>246ko</taille>
        </imPlGr>
    </im>
</infoDoc>
            """
            ),
        )

        url = article_detail_url(article)
        html = Client().get(url).content.decode()
        dom = BeautifulSoup(html, "html.parser")

        fi1 = dom.find("figure", {"id": "fi1"}).find("img").decode()
        assert (
            '<img alt="Modèle intégrateur : les mécanismes du façonnement des normes par la '
            'sphère médiatique" class="lazyload img-responsive" data-aspectratio="863/504" '
            'data-srcset="/fr/revues/journal/2000-issue/article/media/2135184.png 863w" '
            'height="504" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1H'
            'AwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=" width="863"/>' == fi1
        )

    def test_table_groups_display(self):
        article = ArticleFactory(
            from_fixture="1061713ar",
            localidentifier="article",
            issue__year="2000",
            issue__localidentifier="issue",
            issue__journal__code="journal",
            issue__journal__open_access=True,
        )
        url = article_detail_url(article)
        html = Client().get(url).content.decode()
        dom = BeautifulSoup(html, "html.parser")
        grtableau = dom.find_all("div", {"class": "grtableau"})[0]
        figures = grtableau.find_all("figure")
        # Check that the table group is displayed.
        assert grtableau.attrs.get("id") == "gt1"
        # Check that the tables are displayed inside the table group.
        assert figures[0].attrs.get("id") == "ta2"
        assert figures[1].attrs.get("id") == "ta3"
        assert figures[2].attrs.get("id") == "ta4"
        # Check that the table images are displayed inside the tables.
        assert len(figures[0].find_all("img", {"class": "img-responsive"})) == 1
        assert len(figures[1].find_all("img", {"class": "img-responsive"})) == 1
        assert len(figures[2].find_all("img", {"class": "img-responsive"})) == 1
        # Check that the table legends are displayed inside the tables.
        assert len(figures[0].find_all("p", {"class": "alinea"})) == 1
        assert len(figures[1].find_all("p", {"class": "alinea"})) == 2
        assert len(figures[2].find_all("p", {"class": "alinea"})) == 4

    def test_table_groups_display_with_table_no(self):
        article = ArticleFactory(
            from_fixture="1060065ar",
            localidentifier="article",
            issue__year="2000",
            issue__localidentifier="issue",
            issue__journal__code="journal",
            issue__journal__open_access=True,
        )
        url = article_detail_url(article)
        html = Client().get(url).content.decode()
        dom = BeautifulSoup(html, "html.parser")
        grtableau = dom.find_all("div", {"class": "grtableau"})[0]
        figures = grtableau.find_all("figure")
        # Check that the table group is displayed.
        assert grtableau.attrs.get("id") == "gt1"
        # Check that the tables are displayed inside the table group.
        assert figures[0].attrs.get("id") == "ta2"
        assert figures[1].attrs.get("id") == "ta3"
        # Check that the table numbers are displayed.
        assert figures[0].find_all("p", {"class": "no"})[0].text == "2A"
        assert figures[1].find_all("p", {"class": "no"})[0].text == "2B"

    def test_figure_back_arrow_is_displayed_when_theres_no_number_or_title(self):
        article = ArticleFactory(
            from_fixture="1031003ar",
            issue__journal__open_access=True,
        )
        url = article_detail_url(article)
        html = Client().get(url).content.decode()
        # Check that the arrow to go back to the figure is present event if there's no figure
        # number or caption.
        assert (
            '<figure class="tableau" id="lita7"><figcaption><p class="allertexte">'
            '<a href="#ta7"><span class="arrow arrow-bar is-top"></span></a></p>'
            "</figcaption>" in html
        )

    def test_figure_groups_numbers_display_in_figure_list(self):
        article = ArticleFactory(
            from_fixture="1058470ar",
            localidentifier="article",
            issue__year="2000",
            issue__localidentifier="issue",
            issue__journal__code="journal",
            issue__journal__open_access=True,
        )
        url = article_detail_url(article)
        html = Client().get(url).content.decode()
        # Check that the figure numbers are displayed in the figure list for figure groups.
        assert (
            '<div class="grfigure" id="ligf1">\n<div class="grfigure-caption">\n'
            '<p class="allertexte"><a href="#gf1"><span class="arrow arrow-bar is-top"></span>'
            '</a></p>\n<p class="no">Figures 1 - 2</p>' in html
        )

    def test_figcaption_display_for_figure_groups_and_figures(self):
        article = ArticleFactory(
            from_fixture="1060169ar",
            issue__journal__open_access=True,
        )
        url = article_detail_url(article)
        html = Client().get(url).content.decode()
        # Check that figure group caption and the figure captions are displayed.
        assert (
            '<div class="grfigure-caption">\n<p class="allertexte"><a href="#gf1">'
            '<span class="arrow arrow-bar is-top"></span></a></p>\n'
            '<p class="no">Figure 1</p>\n<div class="legende"><p class="legende">'
            '<strong class="titre">RMF frequencies in German data</strong>'
            "</p></div>\n</div>" in html
        )
        assert (
            '<figcaption><p class="legende"><strong class="titre">German non-mediated</strong>'
            "</p></figcaption>" in html
        )
        assert (
            '<figcaption><p class="legende"><strong class="titre">German interpreted'
            "</strong></p></figcaption>" in html
        )

    def test_display_license_img(self):
        article = ArticleFactory(
            from_fixture="1059871ar",
            issue__journal__open_access=True,
        )
        url = article_detail_url(article)
        html = Client().get(url).content.decode()
        assert (
            '<img src="http://licensebuttons.net/l/by/4.0/88x31.png" id="" alt="forme: ">' in html
        )

    def test_existance_of_continuation_mention_in_split_figure(self):
        article = ArticleFactory(
            from_fixture="1056317ar",
            issue__journal__open_access=True,
        )
        url = article_detail_url(article)
        html = Client().get(url).content.decode()
        assert '<p class="no-continuation">Tableau\xa04\xa0<span>(suite)</span></p>' in html

    def test_existance_of_continuation_mention_in_split_table(self):
        article = ArticleFactory(
            from_fixture="1058427ar",
            issue__journal__open_access=True,
        )
        url = article_detail_url(article)
        html = Client().get(url).content.decode()
        assert (
            '<p class="no-continuation"><span class="majuscule">Graphique 3</span>\xa0'
            "<span>(suite)</span></p>" in html
        )

    @pytest.mark.parametrize(
        "localidentifier, expected_result",
        (
            ("1073992ar", True),
            ("1073989ar", False),
        ),
    )
    def test_pdf_link_in_toc(self, localidentifier, expected_result):
        article = ArticleFactory(
            from_fixture=localidentifier,
            with_pdf=True,
        )
        url = reverse(
            "public:journal:article_summary",
            kwargs={
                "journal_code": article.issue.journal.code,
                "issue_slug": article.issue.volume_slug,
                "issue_localid": article.issue.localidentifier,
                "localid": article.localidentifier,
            },
        )
        html = Client().get(url).content.decode()
        pdf_link = '<a href="#pdf-viewer" id="pdf-viewer-menu-link">Texte intégral (PDF)</a>'
        assert (pdf_link in html) is expected_result

    def test_article_multilingual_titles(self):
        article = ArticleFactory(
            from_fixture="1059303ar",
        )
        url = article_detail_url(article)
        html = Client().get(url).content.decode()
        # Check that paral titles are displayed in the article header.
        assert (
            '<span class="titreparal">Détection d’ADN d’<em>Ophiostoma ulmi</em> '
            "introgressé naturellement        dans les régions entourant les loci contrôlant "
            "la pathogénie et le type sexuel chez        <em>O. novo-ulmi</em></span>" in html
        )
        # Check that paral titles are not displayed in summary section.
        assert (
            '<h4><span class="title">Détection d’ADN d’<em>Ophiostoma ulmi</em> introgressé '
            "naturellement dans les régions entourant les loci contrôlant la pathogénie et le "
            "type sexuel chez <em>O. novo-ulmi</em></span></h4>" not in html
        )

    def test_authors_more_information_for_author_with_suffix_and_no_affiliation(self):
        article = ArticleFactory(
            from_fixture="1059571ar",
        )
        url = article_detail_url(article)
        html = Client().get(url).content.decode()
        # Check that more information akkordion is displayed for author with suffix and
        # no affiliation.
        assert (
            '<ul class="akkordion-content unstyled"><li class="auteur-affiliation"><p>'
            "<strong>Guy\n      Sylvestre, o.c.</strong></p></li></ul>" in html
        )

    def test_journal_multilingual_titles_in_citations(self):
        issue = IssueFactory(year="2019")
        repository.api.set_publication_xml(
            issue.get_full_identifier(),
            open("tests/fixtures/issue/ri04376.xml", "rb").read(),
        )
        article = ArticleFactory(
            localidentifier="article",
            issue=issue,
        )
        url = article_detail_url(article)
        html = Client().get(url).content.decode()
        # Check that the journal name is displayed in French and English (Relations industrielles
        # / Industrial Relations).
        assert (
            '<dd id="id_cite_mla_article" class="cite-mla">\n        Pratt, Lynda. '
            "«&nbsp;Robert Southey, Writing and Romanticism.&nbsp;» <em>Relations "
            "industrielles / Industrial Relations</em>, volume 73, numéro 4, automne 2018. "
            "https://doi.org/10.7202/009255ar\n      </dd>" in html
        )
        assert (
            '<dd id="id_cite_apa_article" class="cite-apa">\n        '
            "Pratt, L. (2019). Robert Southey, Writing and Romanticism. "
            "<em>Relations industrielles / Industrial Relations</em>. "
            "https://doi.org/10.7202/009255ar\n      </dd>" in html
        )
        assert (
            '<dd id="id_cite_chicago_article" class="cite-chicago">\n        '
            "Pratt, Lynda «&nbsp;Robert Southey, Writing and Romanticism&nbsp;». "
            "<em>Relations industrielles / Industrial Relations</em> (2019). "
            "https://doi.org/10.7202/009255ar\n      </dd>" in html
        )

    @pytest.mark.parametrize(
        "fixture, url_name, expected_result",
        (
            # Multilingual journals should have all titles in citations.
            (
                "ri04376",
                "public:journal:article_citation_enw",
                "%J Relations industrielles / Industrial Relations",
            ),
            (
                "ri04376",
                "public:journal:article_citation_ris",
                "JO  - Relations industrielles / Industrial Relations",
            ),
            (
                "ri04376",
                "public:journal:article_citation_bib",
                'journal="Relations industrielles / Industrial Relations",',
            ),
            # Sub-titles should not be in citations.
            (
                "im03868",
                "public:journal:article_citation_enw",
                "%J Intermédialités / Intermediality",
            ),
            (
                "im03868",
                "public:journal:article_citation_ris",
                "JO  - Intermédialités / Intermediality",
            ),
            (
                "im03868",
                "public:journal:article_citation_bib",
                'journal="Intermédialités / Intermediality',
            ),
        ),
    )
    def test_journal_multilingual_titles_in_article_citation_views(
        self, fixture, url_name, expected_result
    ):
        issue = IssueFactory()
        repository.api.set_publication_xml(
            issue.get_full_identifier(),
            open("tests/fixtures/issue/{}.xml".format(fixture), "rb").read(),
        )
        article = ArticleFactory(
            issue=issue,
        )
        url = reverse(
            url_name,
            kwargs={
                "journal_code": article.issue.journal.code,
                "issue_slug": article.issue.volume_slug,
                "issue_localid": article.issue.localidentifier,
                "localid": article.localidentifier,
            },
        )
        citation = Client().get(url).content.decode()
        # Check that the journal name is displayed in French and English (Relations industrielles /
        # Industrial Relations).
        assert expected_result in citation

    def test_doi_with_extra_space(self):
        article = ArticleFactory(
            from_fixture="1009368ar",
        )
        url = article_detail_url(article)
        html = Client().get(url).content.decode()
        # Check that extra space around DOIs is stripped.
        assert '<meta name="citation_doi" content="https://doi.org/10.7202/1009368ar" />' in html
        assert '<a href="https://doi.org/10.7202/1009368ar" class="clipboard-data">' in html

    def test_unicode_combining_characters(self):
        article = ArticleFactory(
            from_fixture="1059577ar",
        )
        url = article_detail_url(article)
        html = Client().get(url).content.decode()
        # Pre-combined character is present (ă = ă)
        assert "<em>Studii de lingvistică</em>" in html
        # Combining character is not present (ă = a + ˘)
        assert "<em>Studii de lingvistică</em>" not in html

    def test_acknowledgements_and_footnotes_sections_order(self):
        article = ArticleFactory(
            from_fixture="1060048ar",
            issue__journal__open_access=True,
        )
        url = article_detail_url(article)
        html = Client().get(url).content.decode()
        dom = BeautifulSoup(html, "html.parser")
        partiesann = dom.find_all("section", {"class": "partiesann"})[0]
        sections = partiesann.find_all("section")
        # Check that acknowledgements are displayed before footnotes.
        assert sections[0].attrs["id"] == "merci"
        assert sections[1].attrs["id"] == "grnote"

    def test_abstracts_and_keywords(self):
        article = ArticleFactory()
        with repository.api.open_article(article.pid) as wrapper:
            wrapper.set_abstracts([{"lang": "fr", "content": "Résumé français"}])
            wrapper.set_abstracts([{"lang": "en", "content": "English abstract"}])
            wrapper.add_keywords("es", ["Palabra clave en español"])
            wrapper.add_keywords("fr", ["Mot-clé français"])
        url = article_detail_url(article)
        html = Client().get(url).content.decode()
        dom = BeautifulSoup(html, "html.parser")
        grresume = dom.find_all("section", {"class": "grresume"})[0]
        resumes = grresume.find_all("section", {"class": "resume"})
        keywords = grresume.find_all("div", {"class": "keywords"})
        # Make sure the main abstract (English) appears first, even though it's in second position
        # in the XML.
        assert (
            resumes[0].decode() == '<section class="resume" id="resume-en"><h3>Abstract</h3>\n'
            '<p class="alinea"><em>English abstract</em></p></section>'
        )
        # Make sure the French keywords appear in the French abstract section.
        assert (
            resumes[1].decode() == '<section class="resume" id="resume-fr"><h3>Résumé</h3>\n'
            '<p class="alinea"><em>Résumé français</em></p>\n'
            '<div class="keywords">\n<p><strong>Mots-clés :</strong>'
            '</p>\n<ul><li class="keyword">Mot-clé français</li></ul>'
            "\n</div></section>"
        )
        # Make sure the French keywords appear first since there is no English keywords and no
        # Spanish abstract.
        assert (
            keywords[0].decode() == '<div class="keywords">\n<p><strong>Mots-clés :</strong>'
            '</p>\n<ul><li class="keyword">Mot-clé français</li>'
            "</ul>\n</div>"
        )
        # Make sure the Spanish keywords are displayed even though there is no Spanish abstract.
        assert (
            keywords[1].decode() == '<div class="keywords">\n<p><strong>Palabras clave:'
            '</strong></p>\n<ul><li class="keyword">Palabra clave en '
            "español</li></ul>\n</div>"
        )

    @pytest.mark.parametrize(
        "article_type, expected_string",
        (
            ("compterendu", "Un compte rendu de la revue"),
            ("article", "Un article de la revue"),
        ),
    )
    def test_review_article_explanatory_note(self, article_type, expected_string):
        article = ArticleFactory(type=article_type)
        url = article_detail_url(article)
        html = Client().get(url).content.decode()
        dom = BeautifulSoup(html, "html.parser")
        div = dom.find_all("div", {"class": "doc-head__metadata"})[1]
        note = (
            "Ce document est le compte-rendu d'une autre oeuvre tel qu'un livre ou un "
            "film. L'oeuvre originale discutée ici n'est pas disponible sur cette plateforme."
        )
        assert expected_string in div.decode()
        if article_type == "compterendu":
            assert note in div.decode()
        else:
            assert note not in div.decode()

    def test_verbatim_poeme_lines(self):
        article = ArticleFactory(
            from_fixture="1062061ar",
            issue__journal__open_access=True,
        )
        url = article_detail_url(article)
        html = Client().get(url).content.decode()
        dom = BeautifulSoup(html, "html.parser")
        poeme = dom.find("blockquote", {"class": "verbatim poeme"})
        # Check that poems lines are displayed in <p>.
        assert (
            poeme.decode() == '<blockquote class="verbatim poeme">\n<div class="bloc">\n<p '
            'class="ligne">Jour de larme, </p>\n<p class="ligne">jour où '
            'les coupables se réveilleront</p>\n<p class="ligne">pour '
            'entendre leur jugement,</p>\n<p class="ligne">alors, ô Dieu, '
            'pardonne-leur et leur donne le repos.</p>\n<p class="ligne">'
            "Jésus, accorde-leur le repos.</p>\n</div>\n</blockquote>"
        )

    def test_verbatim_poeme_horizontal_align(self):
        article = ArticleFactory(
            from_fixture="1070671ar",
            issue__journal__open_access=True,
        )
        url = article_detail_url(article)
        html = Client().get(url).content.decode()
        dom = BeautifulSoup(html, "html.parser")
        poeme = dom.find("blockquote", {"class": "verbatim poeme"}).decode()
        # Check that poems lines are centered (align-center).
        assert (
            poeme == '<blockquote class="verbatim poeme">\n'
            '<div class="bloc align align-center">\n'
            '<p class="ligne">On the land</p>\n'
            "</div>\n"
            '<div class="bloc align align-center">\n'
            '<p class="ligne">On the water</p>\n'
            "</div>\n"
            '<div class="bloc align align-center">\n'
            '<p class="ligne">Held in <span class="majuscule">Senćoŧen\n'
            "								</span>kinship</p>\n"
            "</div>\n"
            '<div class="bloc align align-center">\n'
            '<p class="ligne">Today is the future</p>\n'
            "</div>\n"
            '<div class="bloc align align-center">\n'
            '<p class="ligne">It belongs to the next generations</p>\n'
            "</div>\n"
            '<div class="bloc align align-center">\n'
            '<p class="ligne">of learners — dreamers — healers</p>\n'
            "</div>\n"
            '<div class="bloc align align-center">\n'
            '<p class="ligne">Maybe one day we will move beyond territorial\n'
            "								acknowledgement</p>\n"
            "</div>\n"
            '<div class="bloc align align-center">\n'
            '<p class="ligne">and gather here in a good way</p>\n'
            "</div>\n"
            '<div class="bloc align align-center">\n'
            '<p class="ligne">so that the land and their kin</p>\n'
            "</div>\n"
            '<div class="bloc align align-center">\n'
            '<p class="ligne">can introduce themselves.</p>\n'
            "</div>\n"
            "</blockquote>"
        )

    def test_grfigure_caption_position(self):
        article = ArticleFactory(
            from_fixture="1062105ar",
            issue__journal__open_access=True,
        )
        url = article_detail_url(article)
        html = Client().get(url).content.decode()
        dom = BeautifulSoup(html, "html.parser")
        grfigure = dom.find("div", {"id": "gf1"})
        grfigure_caption = grfigure.find_all("div", {"class": "grfigure-caption"})[0]
        grfigure_legende = grfigure.find_all("div", {"class": "grfigure-legende"})[0]
        assert (
            grfigure_caption.decode() == '<div class="grfigure-caption">\n<p class="no">'
            'Figure 1</p>\n<div class="legende"></div>\n</div>'
        )
        assert (
            grfigure_legende.decode() == '<div class="grfigure-legende">\n<p class="alinea">'
            "<sup>a</sup> Hommes et femmes des générations "
            "enquêtées       (1930-1950 résidant en "
            "Île-de-France en 1999) et leurs parents.</p>\n"
            '<p class="alinea"><sup>b</sup> L’interprétation de '
            "cette figure se fait par       exemple de la "
            "manière suivante : Parmi les Ego hommes de "
            "profession       « indépendants », 44 % ont déclaré "
            "que la profession principale de leur père       "
            "était indépendant, 22,5 % ouvrier, 11,9 % cadre, "
            "etc. L’origine « père       indépendant » est "
            "nettement surreprésentée chez les Ego hommes "
            "indépendants.       C’est aussi l’origine la plus "
            "fréquente pour les Ego femmes indépendantes       "
            "(31,5 %), suivie par un père cadre (28,7 %).</p>\n"
            "</div>"
        )

    def test_no_liensimple_in_toc_heading(self):
        article = ArticleFactory(
            from_fixture="1062434ar",
            issue__journal__open_access=True,
        )
        url = article_detail_url(article)
        html = Client().get(url).content.decode()
        dom = BeautifulSoup(html, "html.parser")
        li = dom.find("li", {"class": "article-toc--body"}).find("ul").find_all("li")
        # Check that liensimple nodes are not displayed as links in TOC headings.
        assert (
            li[1].decode() == '<li><a href="#s1n4">«\xa0D’une vaine dispute – La Musique '
            "plaisir de l’esprit ou jouissance sensuelle\xa0» par         "
            'Charles Koechlin, (<em><span class="souligne">La Revue '
            "musicale,           1921</span></em>)</a></li>"
        )
        assert (
            li[2].decode() == '<li><a href="#s1n6">« Réponse à quelques objections » par '
            'Désiré Pâque (<em><span class="souligne">La Revue '
            "musicale,           1935</span></em>)</a></li>"
        )

    @pytest.mark.parametrize("number_related_articles", (0, 3, 4, 5))
    def test_related_articles_multiple_issues_in_journal(self, number_related_articles):
        journal = JournalFactory()
        issue1 = IssueFactory(journal=journal)
        issue2 = IssueFactory(journal=journal)
        for _ in range(number_related_articles):
            ArticleFactory(
                issue=issue2,
                add_to_fedora_issue=True,
                html_url="/test_url",
            )
        # Create the current article, which should not appear in the related articles.
        current_article = ArticleFactory(issue=issue1, localidentifier="current_article")
        # Get the response.
        url = article_detail_url(current_article)
        html = Client().get(url).content
        # Get the HTML.
        dom = BeautifulSoup(html, "html.parser")
        footer = dom.find("footer", {"class": "container"})
        if number_related_articles == 0:
            # Since there are no related articles there is no footer
            assert footer is None
        else:
            # There should be 4 (or less) related articles in the footer
            assert len(footer.find_all("article")) == min(4, number_related_articles)
            # The current article should not be in the related articles.
            assert "current_article" not in footer.decode()

    def test_related_articles_internal_issues(self, monkeypatch):
        journal = JournalFactory()
        issue1 = IssueFactory(journal=journal)
        issue2 = IssueFactory(journal=journal)
        for _ in range(4):
            ArticleFactory(
                issue=issue2,
                add_to_fedora_issue=True,
                html_url="/internal_url",
            )
        # Create the current article, which should not appear in the related articles.
        current_article = ArticleFactory(issue=issue1, localidentifier="current_article")
        # Get the response.
        url = article_detail_url(current_article)
        html = Client().get(url).content
        # Get the HTML.
        dom = BeautifulSoup(html, "html.parser")
        footer = dom.find("footer", {"class": "container"})
        # Assert that the internal relative url is present
        assert "/internal_url" in footer.decode()

    def test_related_articles_external_issues(self, monkeypatch):
        journal = JournalFactory()
        issue1 = IssueFactory(journal=journal)
        issue2 = IssueFactory(journal=journal)
        for _ in range(4):
            ArticleFactory(
                issue=issue2,
                add_to_fedora_issue=True,
                html_url="https://external_url/",
            )
        # Create the current article, which should not appear in the related articles.
        current_article = ArticleFactory(issue=issue1, localidentifier="current_article")
        # Get the response.
        url = article_detail_url(current_article)
        html = Client().get(url).content
        # Get the HTML.
        dom = BeautifulSoup(html, "html.parser")
        footer = dom.find("footer", {"class": "container"})
        # Assert that the external absolute url is present
        assert "https://external_url/" in footer.decode()

    def test_related_articles_single_issue_in_journal(self):
        issue = IssueFactory()
        for _ in range(4):
            ArticleFactory(issue=issue)
        # Create the current article, which should not appear in the related articles.
        current_article = ArticleFactory(issue=issue)
        # Get the response.
        url = article_detail_url(current_article)
        html = Client().get(url).content
        # Get the HTML.
        dom = BeautifulSoup(html, "html.parser")
        footer = dom.find("footer", {"class": "container"})
        # Since there is only one issue we don't have related issues
        assert footer is None

    @pytest.mark.parametrize(
        "with_pdf, pages, has_abstracts, open_access, expected_result",
        (
            # If there's no PDF, there's no need to include `can_display_first_pdf_page` in the
            # context.
            (False, [], False, True, False),
            # If the article has abstracts, there's no need to include `can_display_first_pdf_page`
            # in the context.
            (True, [1, 2], True, True, False),
            # If content access is granted, `can_display_first_pdf_page` should always be True.
            (True, [1], False, True, True),
            (True, [1, 2], False, True, True),
            # If content access is not granted, `can_display_first_pdf_page` should only be True if
            # the PDF has more than one page.
            (True, [1], False, False, False),
            (True, [1, 2], False, False, True),
        ),
    )
    def test_can_display_first_pdf_page(
        self,
        with_pdf,
        pages,
        has_abstracts,
        open_access,
        expected_result,
        monkeypatch,
    ):
        monkeypatch.setattr(fitz.Document, "__len__", lambda p: len(pages))
        article = ArticleFactory(
            issue__journal__open_access=open_access,
            with_pdf=with_pdf,
        )
        if has_abstracts:
            with repository.api.open_article(article.pid) as wrapper:
                wrapper.set_abstracts([{"lang": "fr", "content": "Résumé"}])
        url = article_detail_url(article)
        response = Client().get(url)
        if not with_pdf or has_abstracts:
            assert "can_display_first_pdf_page" not in response.context.keys()
        else:
            assert response.context["can_display_first_pdf_page"] == expected_result

    @pytest.mark.parametrize("open_access", (True, False))
    @pytest.mark.parametrize(
        "url_name",
        (
            "public:journal:article_detail",
            "public:journal:article_summary",
        ),
    )
    def test_complete_processing_article_with_abstracts(self, url_name, open_access):
        article = ArticleFactory(
            from_fixture="1058611ar",
            issue__journal__open_access=open_access,
        )
        url = reverse(
            url_name,
            kwargs={
                "journal_code": article.issue.journal.code,
                "issue_slug": article.issue.volume_slug,
                "issue_localid": article.issue.localidentifier,
                "localid": article.localidentifier,
            },
        )
        html = Client().get(url).content.decode()
        dom = BeautifulSoup(html, "html.parser")
        full_article = dom.find("div", {"class": "full-article"})
        # Abstracts should be displayed in all cases.
        assert full_article.find_all("section", {"id": "resume"})
        # The article body should only be displayed on detail page if content access is granted.
        if open_access and url_name == "public:journal:article_detail":
            assert full_article.find_all("section", {"id": "corps"})
        else:
            assert not full_article.find_all("section", {"id": "corps"})
        # PDF, PDF first page or 600 first words should never be displayed because we have complete
        # processing with abstracts.
        assert not full_article.find_all("section", {"id": "pdf"})
        assert not full_article.find_all("section", {"id": "first-pdf-page"})
        assert not full_article.find_all("section", {"id": "first-600-words"})

    @pytest.mark.parametrize("open_access", (True, False))
    @pytest.mark.parametrize(
        "url_name",
        (
            "public:journal:article_detail",
            "public:journal:article_summary",
        ),
    )
    def test_complete_processing_article_without_abstracts(self, url_name, open_access):
        article = ArticleFactory(
            from_fixture="1005860ar",
            issue__journal__open_access=open_access,
        )
        url = reverse(
            url_name,
            kwargs={
                "journal_code": article.issue.journal.code,
                "issue_slug": article.issue.volume_slug,
                "issue_localid": article.issue.localidentifier,
                "localid": article.localidentifier,
            },
        )
        html = Client().get(url).content.decode()
        dom = BeautifulSoup(html, "html.parser")
        full_article = dom.find("div", {"class": "full-article"})
        # Abstracts should not be displayed because we have none.
        assert not full_article.find_all("section", {"id": "resume"})
        # The article body should only be displayed on detail page if content access is granted.
        if open_access and url_name == "public:journal:article_detail":
            assert full_article.find_all("section", {"id": "corps"})
        else:
            assert not full_article.find_all("section", {"id": "corps"})
        # The first 600 words should only be displayed on summary page or if content access is not
        # granted.
        if not open_access or url_name == "public:journal:article_summary":
            assert full_article.find_all("section", {"id": "first-600-words"})
        else:
            assert not full_article.find_all("section", {"id": "first-600-words"})
        # PDF or PDF first page should never be displayed because we have complete processing.
        assert not full_article.find_all("section", {"id": "pdf"})
        assert not full_article.find_all("section", {"id": "first-pdf-page"})

    @pytest.mark.parametrize("open_access", (True, False))
    @pytest.mark.parametrize(
        "url_name",
        (
            "public:journal:article_detail",
            "public:journal:article_summary",
        ),
    )
    def test_minimal_processing_article_with_abstracts(self, url_name, open_access):
        article = ArticleFactory(
            from_fixture="602354ar",
            issue__journal__open_access=open_access,
            with_pdf=True,
        )
        url = reverse(
            url_name,
            kwargs={
                "journal_code": article.issue.journal.code,
                "issue_slug": article.issue.volume_slug,
                "issue_localid": article.issue.localidentifier,
                "localid": article.localidentifier,
            },
        )
        html = Client().get(url).content.decode()
        dom = BeautifulSoup(html, "html.parser")
        full_article = dom.find("div", {"class": "full-article"})
        # Abstracts should be displayed in all cases.
        assert full_article.find_all("section", {"id": "resume"})
        # The article PDF should only be displayed on detail page if content access is granted.
        if open_access and url_name == "public:journal:article_detail":
            assert full_article.find_all("section", {"id": "pdf"})
        else:
            assert not full_article.find_all("section", {"id": "pdf"})
        # Article body, 600 first words or PDF first page should never be displayed because we have
        # minimal processing with abstracts.
        assert not full_article.find_all("section", {"id": "corps"})
        assert not full_article.find_all("section", {"id": "first-600-words"})
        assert not full_article.find_all("section", {"id": "first-pdf-page"})

    @pytest.mark.parametrize("open_access", (True, False))
    @pytest.mark.parametrize(
        "url_name",
        (
            "public:journal:article_detail",
            "public:journal:article_summary",
        ),
    )
    @pytest.mark.parametrize("pages", ([1], [1, 2]))
    def test_minimal_processing_article_without_abstracts(self, pages, url_name, open_access):
        article = ArticleFactory(
            from_fixture="1056823ar",
            issue__journal__open_access=open_access,
            with_pdf=True,
        )
        url = reverse(
            url_name,
            kwargs={
                "journal_code": article.issue.journal.code,
                "issue_slug": article.issue.volume_slug,
                "issue_localid": article.issue.localidentifier,
                "localid": article.localidentifier,
            },
        )
        html = Client().get(url).content.decode()
        dom = BeautifulSoup(html, "html.parser")
        full_article = dom.find("div", {"class": "full-article"})
        # Abstracts should not be displayed because we have none.
        assert not full_article.find_all("section", {"id": "resume"})
        # The article PDF should only be displayed on detail page if content access is granted.
        if open_access and url_name == "public:journal:article_detail":
            assert full_article.find_all("section", {"id": "pdf"})
        else:
            assert not full_article.find_all("section", {"id": "pdf"})
        # The article PDF first page should only be displayed on summary page or if content access
        # is not granted.
        if not open_access or url_name == "public:journal:article_summary":
            assert full_article.find_all("section", {"id": "first-pdf-page"})
        else:
            assert not full_article.find_all("section", {"id": "first-pdf-page"})
        # Article body or 600 first words should never be displayed because we have minimal
        # processing.
        assert not full_article.find_all("section", {"id": "corps"})
        assert not full_article.find_all("section", {"id": "first-600-words"})

    @pytest.mark.parametrize("open_access", (True, False))
    @pytest.mark.parametrize(
        "url_name",
        (
            "public:journal:article_detail",
            "public:journal:article_summary",
        ),
    )
    def test_minimal_processing_article_without_abstracts_and_with_only_one_page(
        self, url_name, open_access, monkeypatch
    ):
        monkeypatch.setattr(fitz.Document, "__len__", lambda p: 1)
        article = ArticleFactory(
            from_fixture="1056823ar",
            issue__journal__open_access=open_access,
            with_pdf=True,
        )
        url = reverse(
            url_name,
            kwargs={
                "journal_code": article.issue.journal.code,
                "issue_slug": article.issue.volume_slug,
                "issue_localid": article.issue.localidentifier,
                "localid": article.localidentifier,
            },
        )
        html = Client().get(url).content.decode()
        dom = BeautifulSoup(html, "html.parser")
        full_article = dom.find("div", {"class": "full-article"})
        # Abstracts should not be displayed because we have none.
        assert not full_article.find_all("section", {"id": "resume"})
        # The article PDF should only be displayed on detail page if content access is granted.
        if open_access and url_name == "public:journal:article_detail":
            assert full_article.find_all("section", {"id": "pdf"})
        else:
            assert not full_article.find_all("section", {"id": "pdf"})
        # The article PDF first page should only be displayed on summary page if content access is
        # granted because the PDF has only one page.
        if open_access and url_name == "public:journal:article_summary":
            assert full_article.find_all("section", {"id": "first-pdf-page"})
        else:
            assert not full_article.find_all("section", {"id": "first-pdf-page"})
        # Article body or 600 first words should never be displayed because we have minimal
        # processing.
        assert not full_article.find_all("section", {"id": "corps"})
        assert not full_article.find_all("section", {"id": "first-600-words"})

    @pytest.mark.parametrize(
        "has_abstracts, expected_alert",
        (
            (True, "Seul le résumé sera affiché."),
            (False, "Seuls les 600 premiers mots du texte seront affichés."),
        ),
    )
    def test_complete_processing_article_content_access_not_granted_alert(
        self,
        has_abstracts,
        expected_alert,
    ):
        article = ArticleFactory(issue__journal__open_access=False)
        if has_abstracts:
            with repository.api.open_article(article.pid) as wrapper:
                wrapper.set_abstracts([{"lang": "fr", "content": "Résumé"}])
        url = article_detail_url(article)
        html = Client().get(url).content.decode()
        assert expected_alert in html

    @pytest.mark.parametrize(
        "has_abstracts, pages, expected_alert",
        (
            (True, [1, 2], "Seul le résumé sera affiché."),
            (True, [1], "Seul le résumé sera affiché."),
            (False, [1, 2], "Seule la première page du PDF sera affichée."),
            (False, [1], "Seule la première page du PDF sera affichée."),
        ),
    )
    def test_minimal_processing_article_content_access_not_granted_alert(
        self,
        has_abstracts,
        pages,
        expected_alert,
        monkeypatch,
    ):
        monkeypatch.setattr(fitz.Document, "__len__", lambda p: len(pages))
        article = ArticleFactory(
            from_fixture="1056823ar",
            issue__journal__open_access=False,
            with_pdf=True,
        )
        if has_abstracts:
            with repository.api.open_article(article.pid) as wrapper:
                wrapper.set_abstracts([{"lang": "fr", "content": "Résumé"}])
        url = article_detail_url(article)
        html = Client().get(url).content.decode()
        # The expected alert should only be displayed if there's abstracts or if the PDF has more
        # than one page.
        if has_abstracts or len(pages) > 1:
            assert expected_alert in html
        else:
            assert expected_alert not in html

    @pytest.mark.parametrize(
        "fixture, section_id, expected_title",
        (
            # Articles without specified titles in the XML, default values should be used.
            ("1054008ar", "grnotebio", "Note biographique"),
            ("1054008ar", "grnote", "Notes"),
            ("1059303ar", "merci", "Acknowledgements"),
            # Articles with specified titles in the XML.
            ("009676ar", "grnotebio", "Collaboratrice"),
            ("009381ar", "grnote", "Notas"),
            ("1040250ar", "merci", "Remerciements et financement"),
        ),
    )
    def test_article_annex_section_titles(self, fixture, section_id, expected_title):
        article = ArticleFactory(
            from_fixture=fixture,
            issue__journal__open_access=True,
        )
        url = article_detail_url(article)
        html = Client().get(url).content.decode()
        dom = BeautifulSoup(html, "html.parser")
        article_toc = dom.find("nav", {"class": "article-table-of-contents"})
        section = dom.find("section", {"id": section_id})
        assert article_toc.find("a", {"href": "#" + section_id}).text == expected_title
        assert section.find("h2").text == expected_title

    @pytest.mark.parametrize(
        "fixture, expected_title",
        (
            ("009676ar", "Bibliographie"),
            ("1070621ar", "Bibliography"),
            ("1054008ar", "Références"),
        ),
    )
    def test_article_grbiblio_section_titles(self, fixture, expected_title):
        article = ArticleFactory(
            from_fixture=fixture,
            issue__journal__open_access=True,
        )
        url = article_detail_url(article)
        html = Client().get(url).content.decode()
        dom = BeautifulSoup(html, "html.parser")
        article_toc = dom.find("nav", {"class": "article-table-of-contents"})
        section = dom.find("section", {"id": "grbiblio"})
        assert article_toc.find("a", {"href": "#biblio-1"}).text == expected_title
        assert section.find("h2").text == expected_title

    def test_media_object_source(self):
        article = ArticleFactory(
            from_fixture="1065018ar",
            issue__journal__open_access=True,
        )
        url = article_detail_url(article)
        html = Client().get(url).content.decode()
        dom = BeautifulSoup(html, "html.parser")
        media_object = dom.find("figure", {"class": "objet"})
        assert media_object.find("cite", {"class": "source"}).text == "Courtesy of La compagnie"

    def test_media_object_padding_bottom_based_on_aspect_ratio(self):
        article = ArticleFactory(
            from_fixture="1065018ar",
            issue__journal__open_access=True,
        )
        url = article_detail_url(article)
        html = Client().get(url).content.decode()
        dom = BeautifulSoup(html, "html.parser")
        media_object = dom.find("div", {"class": "embed-responsive"})
        assert media_object.get("style") == "padding-bottom: 56.563%"

    @pytest.mark.parametrize(
        "fixture, expected_section_titles",
        (
            (
                "1054008ar",
                [
                    "<h2>Suspension du verbe</h2>",
                    "<h2>Une éthique de l’action</h2>",
                    "<h3>1– Nécessité de limiter l’action.</h3>",
                    "<h3>2– Nécessité de simplifier, c’est-à-dire de réduire à l’essentiel.</h3>",
                    "<h3>3– Nécessité (pour l’homme) de se transformer.</h3>",
                    "<h2>Une «\xa0poéthique\xa0»</h2>",
                    "<h2>L’en avant de la parole</h2>",
                ],
            ),
            (
                "1062105ar",
                [
                    '<h2><span class="majuscule">Introduction</span></h2>',
                    '<h2><span class="majuscule">1. La mesure de la mobilitÉ sociale en France '
                    "et     au QuÉbec</span></h2>",
                    '<h2><span class="majuscule">2. MÉthodes</span></h2>',
                    "<h3>2.1 Présentation des deux enquêtes et des variables professionnelles     "
                    "sélectionnées</h3>",
                    "<h3>2.2 Les codages effectués pour mesurer les transmissions     "
                    "professionnelles</h3>",
                    "<h4><em>2.2.1 Genre et niveau de     compétences</em></h4>",
                    "<h4><em>2.2.2 Catégories     socioprofessionnelles</em></h4>",
                    '<h2><span class="majuscule">3. Évolution de la structure '
                    "socioprofessionnelle     des emplois et transmissions professionnelles au "
                    "sein des     lignÉes</span></h2>",
                    "<h3>3.1 Répartition des positions socioprofessionnelles dans les lignées "
                    "des     générations enquêtées</h3>",
                    "<h3>3.2 Transmissions professionnelles dans les lignées</h3>",
                    '<h2><span class="majuscule">Conclusion</span></h2>',
                ],
            ),
        ),
    )
    def test_article_toc_view(self, fixture, expected_section_titles):
        article = ArticleFactory(
            from_fixture=fixture,
            issue__journal__open_access=True,
        )
        url = reverse(
            "public:journal:article_toc",
            kwargs={
                "journal_code": article.issue.journal.code,
                "issue_slug": article.issue.volume_slug,
                "issue_localid": article.issue.localidentifier,
                "localid": article.localidentifier,
            },
        )
        html = Client().get(url).content.decode()
        for section_title in expected_section_titles:
            assert section_title in html

    @pytest.mark.parametrize(
        "mock_is_external, mock_url, expected_status_code",
        [
            (False, None, 200),
            (True, "http://www.example.com", 301),
        ],
    )
    def test_get_external_issues_are_redirected(
        self, mock_is_external, mock_url, expected_status_code, monkeypatch
    ):
        monkeypatch.setattr(Article, "is_external", mock_is_external)
        monkeypatch.setattr(Article, "url", mock_url)
        article = ArticleFactory()
        url = article_detail_url(article)
        response = Client().get(url)
        assert response.status_code == expected_status_code
        if mock_url:
            assert response.url == mock_url

    def test_marquage_in_affiliations(self):
        article = ArticleFactory(from_fixture="1066010ar")
        url = article_detail_url(article)
        html = Client().get(url).content.decode()
        assert (
            '<li class="auteur-affiliation"><p><strong>Benoit\n      Vaillancourt</strong><br>'
            '<span class="petitecap">C</span><span class="petitecap">élat</span>'
            '<span class="petitecap">, Ipac, </span>Université Laval</p></li>' in html
        )

    @pytest.mark.parametrize(
        "fixture, expected_link",
        (
            # `https://` should be added to URLs that starts with `www`.
            (
                "1038424ar",
                '<a href="https://www.inspq.qc.ca/pdf/publications/1177_RelGazSchisteSante'
                '%20PubRapPreliminaire.pdf" id="ls3" target="_blank">www.inspq.qc.ca/pdf/'
                "publications/1177_RelGazSchisteSante PubRapPreliminaire.pdf</a>",
            ),
            # `https://` should not be added to email addresses.
            (
                "1038424ar",
                '<a href="mailto:yenny.vega.cardenas@umontreal.ca" id="ls1" '
                'target="_blank">yenny.vega.cardenas@umontreal.ca</a>',
            ),
            # Complete URLs should not be altered.
            (
                "1038424ar",
                '<a href="http://www.nytimes.com/2014/12/18/nyregion/cuomo-to-ban-fracking-'
                'in-new-york-state-citing-health-risks.html?_r=0" id="ls4" target="_blank">'
                "http://www.nytimes.com/2014/12/18/nyregion/cuomo-to-ban-fracking-"
                "in-new-york-state-citing-health-risks.html?_r=0</a>",
            ),
            # Links to `http://www.erudit.org` should not have target="_blank".
            (
                "009256ar",
                '<a href="http://www.erudit.org/revue/ron/1998/v/n9" id="ls1">'
                "http://www.erudit.org/revue/ron/1998/v/n9</a>",
            ),
        ),
    )
    def test_liensimple_urls(self, fixture, expected_link):
        article = ArticleFactory(from_fixture=fixture)
        url = article_detail_url(article)
        html = Client().get(url).content.decode()
        assert expected_link in html

    def test_no_white_spaces_around_objetmedia(self):
        article = ArticleFactory(
            from_fixture="1067517ar",
            localidentifier="article",
            issue__year="2020",
            issue__localidentifier="issue",
            issue__journal__code="journal",
            issue__journal__open_access=True,
        )
        url = article_detail_url(article)
        html = Client().get(url).content.decode()
        # No unwanted extra spaces in addition of wanted non-breaking spaces inside quotes.
        assert (
            '«\xa0<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwC'
            'AAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=" '
            'data-srcset="/fr/revues/journal/2020-issue/article/media/2127962n.jpg 16w" '
            'data-aspectratio="0.941176470588235" width="16" height="17" class="lazyload" '
            'id="im10" alt="forme: forme pleine grandeur">\xa0U+1F469 woman\xa0»' in html
        )
        # No unwanted extra spaces inside parentheses.
        assert (
            '(<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAA'
            'C0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=" '
            'data-srcset="/fr/revues/journal/2020-issue/article/media/2127980n.jpg 17w" '
            'data-aspectratio="1.307692307692308" width="17" height="13" class="lazyload" '
            'id="im34" alt="forme: forme pleine grandeur">)' in html
        )
        # No unwanted extra spaces after hashtag.
        assert (
            '#<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAA'
            'C0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=" '
            'data-srcset="/fr/revues/journal/2020-issue/article/media/2127981n.jpg 32w" '
            'data-aspectratio="1.684210526315789" width="32" height="19" class="lazyload" '
            'id="im35" alt="forme: forme pleine grandeur">' in html
        )

    def test_footnote_in_bibliography_title(self):
        article = ArticleFactory(from_fixture="1068385ar")
        url = article_detail_url(article)
        html = Client().get(url).content.decode()
        assert (
            '<h2 id="biblio-1">Bibliographie sélective<a href="#no49" id="re1no49" '
            'class="norenvoi" title="La bibliographie recense exclusivement les travaux cités dans '
            "l’article. En complément, la base de données des logiciels et projets (cf.\xa0note 2) "
            'propose pour l’ensemble des logicie[…]">[49]</a>\n</h2>' in html
        )
        assert '<li><a href="#biblio-1">Bibliographie sélective</a></li>' in html

    def test_organistaion_as_author_is_displayed_in_bold(self):
        article = ArticleFactory(from_fixture="1068900ar")
        url = article_detail_url(article)
        html = Client().get(url).content.decode()
        assert (
            '<li class="auteur-affiliation">'
            "<p><strong>The MAP Research Team</strong></p>"
            "</li>" in html
        )

    def test_appendices_titles_language(self):
        article = ArticleFactory(
            from_fixture="1069092ar",
            issue__journal__open_access=True,
        )
        url = article_detail_url(article)
        html = Client().get(url).content.decode()
        dom = BeautifulSoup(html, "html.parser")
        sections = dom.find_all("section", {"class": "grnotebio"})
        assert len(sections) == 3
        assert sections[0].find("h2").decode() == "<h2>Notes biographiques</h2>"
        assert sections[1].find("h2").decode() == "<h2>Biographical notes</h2>"
        assert sections[2].find("h2").decode() == "<h2>Notas biograficas</h2>"

    def test_do_not_display_label_if_no_volume_and_number(self):
        article = ArticleFactory(
            from_fixture="1059031ar",
            issue__journal__open_access=True,
        )
        url = article_detail_url(article)
        html = Client().get(url).content.decode()
        dom = BeautifulSoup(html, "html.parser")
        span = dom.find("span", {"class": "volumaison"})
        assert span.decode() == '<span class="volumaison">2018</span>'

    @pytest.mark.parametrize(
        "collection_code, expected_document_id",
        (
            ("erudit", "article1"),
            ("unb", "unb:article1"),
        ),
    )
    def test_data_document_id_includes_unb_prefix(self, collection_code, expected_document_id):
        article = ArticleFactory(
            issue__journal__collection__code=collection_code,
            localidentifier="article1",
        )
        url = article_detail_url(article)
        html = Client().get(url).content.decode()
        assert f'data-document-id="{expected_document_id}"' in html

    @override_settings(CACHES=settings.LOCMEM_CACHES)
    def test_subscription_message_is_not_cached(self):
        client = Client()
        article = ArticleFactory(issue__journal__open_access=True)
        JournalAccessSubscriptionFactory(
            type="individual",
            user=UserFactory.create(username="foobar", password="notsecret"),
            journals=[article.issue.journal],
        )

        client.login(username="foobar", password="notsecret")
        response = client.get(article_detail_url(article))
        assert "Vous êtes abonné à cette revue." in response.content.decode()

        client.logout()
        response = client.get(article_detail_url(article))
        assert "Vous êtes abonné à cette revue." not in response.content.decode()

    @pytest.mark.parametrize(
        "issue_localid, article_localid, expected",
        (
            (
                "ritpu1824085",
                "1006396ar",
                [
                    '<meta content="1708-7570" name="citation_issn"/>',
                ],
            ),
            (
                "images1080663",
                "23339ac",
                [
                    '<meta content="0707-9389" name="citation_issn"/>',
                    '<meta content="1923-5097" name="citation_issn"/>',
                ],
            ),
        ),
    )
    def test_issue_issn_print_and_issn_web_display(self, issue_localid, article_localid, expected):
        article = ArticleFactory(localidentifier=article_localid)
        repository.api.set_publication_xml(
            article.issue.get_full_identifier(),
            open(f"tests/fixtures/issue/{issue_localid}.xml", "rb").read(),
        )
        url = article_detail_url(article)
        html = Client().get(url).content.decode()
        dom = BeautifulSoup(html, "html.parser")
        issn_metas = dom.find_all("meta", {"name": "citation_issn"})
        assert len(issn_metas) == len(expected)
        for i, issn in enumerate(issn_metas):
            assert issn.decode() == expected[i]

    def test_display_untitled_article_if_article_has_no_title(self):
        article = ArticleFactory(
            from_fixture="1023079ar",
        )
        url = article_detail_url(article)
        html = Client().get(url).content.decode()
        assert '<span class="titre">[Article sans titre]</span>' in html

    def test_display_organistion_members(self):
        article = ArticleFactory(from_fixture="1077218ar")
        url = article_detail_url(article)
        html = Client().get(url).content.decode()
        dom = BeautifulSoup(html, "html.parser")
        authors = dom.find_all("li", {"class": "auteur-affiliation"})
        assert (
            authors[3].decode()
            == '<li class="auteur-affiliation"><p><strong>Regroupement des Directrices de soins '
            "d’établissements\n        psychiatriques</strong><br/>"
            "<strong>Céline\n      Pilon</strong><br/>"
            "CH Institut Philippe-Pinel, responsable du dossier<br/>"
            "<strong>Diane\n      Benoît</strong><br/>"
            "CH Louis-H. Lafontaine<br/>"
            "<strong>Louise\n      Bérubé</strong><br/>"
            "CH Robert-Giffard<br/>"
            "<strong>Monique\n      Bissonnette</strong><br/>"
            "CH Rivière-des-Prairies<br/>"
            "<strong>Robyne\n      Kershaw-Bellemare</strong><br/>"
            "Hôpital Douglas<br/>"
            "<strong>Louise\n      Letarte</strong><br/>"
            "CH Pierre-Janet</p></li>"
        )

    @pytest.mark.parametrize(
        "fixture, section_id, expected_title, expected_count",
        (
            ("1076454ar", "videos", "<h2>Liste des vidéos</h2>", 3),
            ("1058476ar", "audios", "<h2>Liste des fichiers audio</h2>", 3),
        ),
    )
    def test_display_list_of_videos_and_audio_files(
        self, fixture, section_id, expected_title, expected_count
    ):
        article = ArticleFactory(from_fixture=fixture, issue__journal__open_access=True)
        url = article_detail_url(article)
        html = Client().get(url).content.decode()
        dom = BeautifulSoup(html, "html.parser")
        videos = dom.find("section", {"id": section_id})
        assert videos.find("h2").decode() == expected_title
        assert len(videos.find_all("figure")) == expected_count


class TestArticleRawPdfView:
    def test_can_retrieve_the_pdf_of_existing_articles(self):
        article = ArticleFactory(with_pdf=True, issue__journal__open_access=True)
        url = reverse(
            "public:journal:article_raw_pdf",
            args=(
                article.issue.journal_id,
                article.issue.volume_slug,
                article.issue.localidentifier,
                article.localidentifier,
            ),
        )
        response = Client().get(url)

        assert response.status_code == 200
        assert response["Content-Type"] == "application/pdf"

    @pytest.mark.parametrize(
        "has_pdf_journal, has_pdf_erudit, expected_text",
        [
            (True, True, "Arborescences"),
            (True, False, "Arborescences"),
            (False, True, "Criminologie"),
        ],
    )
    def test_select_journal_produced_pdf_or_erudit_produced_pdf(
        self,
        has_pdf_journal,
        has_pdf_erudit,
        expected_text,
    ):
        # The "Arborecences" pdf was produced by the journal, so we expect to find the word
        # "Arborescences" in the pdf header. The same goes to "Criminologie" that was produced
        # by Érudit. Both words appear only in their correspondent articles.
        article = ArticleFactory(
            with_pdf=has_pdf_journal,
            with_pdf_erudit=has_pdf_erudit,
            issue__journal__open_access=True,
        )
        url = reverse(
            "public:journal:article_raw_pdf",
            args=(
                article.issue.journal_id,
                article.issue.volume_slug,
                article.issue.localidentifier,
                article.localidentifier,
            ),
        )
        response = Client().get(url)

        with fitz.open(stream=io.BytesIO(response.content), filetype="pdf") as f:
            pdf_text = ""
            for page in f:
                pdf_text += page.getText()

        assert expected_text in pdf_text
        assert response.status_code == 200
        assert response["Content-Type"] == "application/pdf"

    def test_cannot_retrieve_the_pdf_of_inexistant_articles(self):
        # Note: as there is no Erudit fedora repository used during the
        # test, any tentative of retrieving the PDF of an article should
        # fail.

        journal_id = "dummy139"
        issue_slug = "test"
        issue_id = "dummy1515298"
        article_id = "1001942du"
        url = reverse(
            "public:journal:article_raw_pdf", args=(journal_id, issue_slug, issue_id, article_id)
        )
        response = Client().get(url)
        assert response.status_code == 404

    @pytest.mark.parametrize(
        "pages, expected_exception",
        [
            ([], True),
            ([1], True),
            ([1, 2], False),
        ],
    )
    def test_can_retrieve_the_firstpage_pdf_of_existing_articles(
        self, pages, expected_exception, monkeypatch
    ):
        monkeypatch.setattr(fitz.Document, "__len__", lambda p: len(pages))
        journal = JournalFactory()
        issue = IssueFactory.create(
            journal=journal, year=2010, date_published=dt.datetime.now() - dt.timedelta(days=1000)
        )
        IssueFactory.create(journal=journal, year=2010, date_published=dt.datetime.now())
        article = ArticleFactory.create(issue=issue, with_pdf=True)
        journal_id = journal.localidentifier
        issue_id = issue.localidentifier
        article_id = article.localidentifier
        url = article_raw_pdf_url(article)
        request = RequestFactory().get(url)
        request.user = AnonymousUser()
        request.session = {}
        request.subscriptions = UserSubscriptions()

        # Raise exception if PDF has less than 2 pages.
        if expected_exception:
            with pytest.raises(PermissionDenied):
                response = ArticleRawPdfFirstPageView.as_view()(
                    request,
                    journal_code=journal_id,
                    issue_slug=issue.volume_slug,
                    issue_localid=issue_id,
                    localid=article_id,
                )
        else:
            response = ArticleRawPdfFirstPageView.as_view()(
                request,
                journal_code=journal_id,
                issue_slug=issue.volume_slug,
                issue_localid=issue_id,
                localid=article_id,
            )

            assert response.status_code == 200
            assert response["Content-Type"] == "application/pdf"

    def test_cannot_be_accessed_if_the_article_is_not_in_open_access(self):
        journal = JournalFactory(open_access=False)
        issue = IssueFactory.create(
            journal=journal, year=dt.datetime.now().year, date_published=dt.datetime.now()
        )
        article = ArticleFactory.create(issue=issue)
        journal_code = journal.code
        issue_id = issue.localidentifier
        article_id = article.localidentifier
        url = article_raw_pdf_url(article)

        request = RequestFactory().get(url)
        request.user = AnonymousUser()
        request.session = {}
        request.subscriptions = UserSubscriptions()

        response = ArticleRawPdfView.as_view()(
            request,
            journal_code=journal_code,
            issue_slug=issue.volume_slug,
            issue_localid=issue_id,
            localid=article_id,
        )

        assert isinstance(response, HttpResponseRedirect)
        assert response.url == article_detail_url(article)

    def test_cannot_be_accessed_if_the_publication_of_the_article_is_not_allowed_by_its_authors(
        self,
    ):  # noqa
        journal = JournalFactory(open_access=False)
        issue = IssueFactory.create(journal=journal, year=2010, date_published=dt.datetime.now())
        article = ArticleFactory.create(issue=issue, publication_allowed=False)
        journal_code = journal.code
        issue_id = issue.localidentifier
        article_id = article.localidentifier
        url = article_raw_pdf_url(article)
        request = RequestFactory().get(url)
        request.user = AnonymousUser()
        request.session = {}
        request.subscriptions = UserSubscriptions()

        response = ArticleRawPdfView.as_view()(
            request,
            journal_code=journal_code,
            issue_slug=issue.volume_slug,
            issue_localid=issue_id,
            localid=article_id,
        )

        assert isinstance(response, HttpResponseRedirect)
        assert response.url == article_detail_url(article)


class TestLegacyUrlsRedirection:
    def test_can_redirect_issue_support_only_volume_and_year(self):
        journal = JournalFactory(code="test")
        issue = IssueFactory(journal=journal, volume="1", number="1", year="2017")
        IssueFactory(journal=issue.journal, volume="1", number="2", year="2017")
        article = ArticleFactory()
        article.issue.volume = "1"
        article.issue.number = "1"
        article.issue.year = "2017"
        article.issue.save()

        article2 = ArticleFactory()
        article2.issue.journal = article.issue.journal
        article2.issue.volume = "1"
        article2.issue.number = "2"
        article2.issue.year = "2017"
        article2.issue.save()
        url = "/revue/{journal_code}/{year}/v{volume}/n/".format(
            journal_code=article.issue.journal.code,
            year=article.issue.year,
            volume=article.issue.volume,
        )

        resp = Client().get(url)

        assert resp.url == reverse(
            "public:journal:issue_detail",
            kwargs=dict(
                journal_code=article2.issue.journal.code,
                issue_slug=article2.issue.volume_slug,
                localidentifier=article2.issue.localidentifier,
            ),
        )

    def test_can_redirect_issue_detail_with_empty_volume(self):
        issue = IssueFactory(number="1", volume="1", year="2017")
        issue2 = IssueFactory(journal=issue.journal, volume="2", number="1", year="2017")
        url = "/revue/{journal_code}/{year}/v/n{number}/".format(
            journal_code=issue.journal.code,
            number=issue.number,
            year=issue.year,
        )

        resp = Client().get(url)

        assert resp.url == reverse(
            "public:journal:issue_detail",
            kwargs=dict(
                journal_code=issue2.journal.code,
                issue_slug=issue2.volume_slug,
                localidentifier=issue2.localidentifier,
            ),
        )

    def test_can_redirect_article_from_legacy_urls(self):
        from django.utils.translation import deactivate_all

        article = ArticleFactory()
        article.issue.volume = "1"
        article.issue.save()

        url = "/revue/{journal_code}/{issue_year}/v{issue_volume}/n/{article_localidentifier}.html".format(  # noqa
            journal_code=article.issue.journal.code,
            issue_year=article.issue.year,
            issue_volume=article.issue.volume,
            article_localidentifier=article.localidentifier,
        )

        resp = Client().get(url)
        assert resp.status_code == 301

        url = (
            "/revue/{journal_code}/{issue_year}/v/n/{article_localidentifier}.html".format(  # noqa
                journal_code=article.issue.journal.code,
                issue_year=article.issue.year,
                article_localidentifier=article.localidentifier,
            )
        )

        resp = Client().get(url)
        assert resp.status_code == 301

        url = "/revue/{journal_code}/{issue_year}/v/n{issue_number}/{article_localidentifier}.html".format(  # noqa
            journal_code=article.issue.journal.code,
            issue_year=article.issue.year,
            issue_number=article.issue.number,
            article_localidentifier=article.localidentifier,
        )

        resp = Client().get(url)

        assert resp.url == article_detail_url(article)
        assert "/fr/" in resp.url
        assert resp.status_code == 301

        deactivate_all()
        resp = Client().get(url + "?lang=en")

        assert resp.url == article_detail_url(article)
        assert "/en/" in resp.url
        assert resp.status_code == 301

        url = "/en/revue/{journal_code}/{issue_year}/v/n{issue_number}/{article_localidentifier}.html".format(  # noqa
            journal_code=article.issue.journal.code,
            issue_year=article.issue.year,
            issue_number=article.issue.number,
            article_localidentifier=article.localidentifier,
        )
        deactivate_all()
        resp = Client().get(url)

        assert resp.url == article_detail_url(article)

        assert "/en/" in resp.url
        assert resp.status_code == 301

    @pytest.mark.parametrize(
        "pattern",
        (
            "/revue/{journal_code}/{year}/v{volume}/n{number}/",
            "/culture/{journal_localidentifier}/{issue_localidentifier}/index.html",
        ),
    )
    def test_can_redirect_issues_from_legacy_urls(self, pattern):
        article = ArticleFactory()
        article.issue.volume = "1"
        article.issue.number = "1"
        article.issue.save()
        url = pattern.format(
            journal_code=article.issue.journal.code,
            year=article.issue.year,
            volume=article.issue.volume,
            number=article.issue.number,
            journal_localidentifier=article.issue.journal.localidentifier,
            issue_localidentifier=article.issue.localidentifier,
            article_localidentifier=article.localidentifier,
        )
        resp = Client().get(url)

        assert resp.url == reverse(
            "public:journal:issue_detail",
            kwargs=dict(
                journal_code=article.issue.journal.code,
                issue_slug=article.issue.volume_slug,
                localidentifier=article.issue.localidentifier,
            ),
        )
        assert resp.status_code == 301

    def test_can_redirect_journals_from_legacy_urls(self):
        article = ArticleFactory()
        article.issue.volume = "1"
        article.issue.number = "1"
        article.issue.save()
        url = "/revue/{code}/".format(
            code=article.issue.journal.code,
        )
        resp = Client().get(url)

        assert resp.url == journal_detail_url(article.issue.journal)
        assert resp.status_code == 301


class TestArticleFallbackRedirection:
    @pytest.fixture(
        params=itertools.product(
            [{"code": "nonexistent"}],
            [
                "legacy_journal:legacy_journal_detail",
                "legacy_journal:legacy_journal_detail_index",
                "legacy_journal:legacy_journal_authors",
                "legacy_journal:legacy_journal_detail_culture",
                "legacy_journal:legacy_journal_detail_culture_index",
                "legacy_journal:legacy_journal_authors_culture",
            ],
        )
    )
    def journal_url(self, request):
        kwargs = request.param[0]
        url = request.param[1]
        return reverse(url, kwargs=kwargs)

    @pytest.fixture(
        params=itertools.chain(
            itertools.product(
                [
                    {
                        "journal_code": "nonexistent",
                        "year": "1974",
                        "v": "7",
                        "n": "1",
                    }
                ],
                ["legacy_journal:legacy_issue_detail", "legacy_journal:legacy_issue_detail_index"],
            ),
            itertools.product(
                [
                    {
                        "journal_code": "nonexistent",
                        "year": "1974",
                        "v": "7",
                        "n": "",
                    }
                ],
                ["legacy_journal:legacy_issue_detail", "legacy_journal:legacy_issue_detail_index"],
            ),
            itertools.product(
                [
                    {
                        "journal_code": "nonexistent",
                        "year": "1974",
                        "v": "7",
                        "n": "",
                    }
                ],
                ["legacy_journal:legacy_issue_detail", "legacy_journal:legacy_issue_detail_index"],
            ),
            itertools.product(
                [{"journal_code": "nonexistent", "localidentifier": "nonexistent"}],
                [
                    "legacy_journal:legacy_issue_detail_culture",
                    "legacy_journal:legacy_issue_detail_culture_index",
                ],
            ),
        )
    )
    def issue_url(self, request):
        kwargs = request.param[0]
        url = request.param[1]
        return reverse(url, kwargs=kwargs)

    @pytest.fixture(
        params=itertools.chain(
            itertools.product(
                [
                    {
                        "journal_code": "nonexistent",
                        "year": 2004,
                        "v": 1,
                        "issue_number": "nonexistent",
                        "localid": "nonexistent",
                        "format_identifier": "html",
                        "lang": "fr",
                    }
                ],
                [
                    "legacy_journal:legacy_article_detail",
                    "legacy_journal:legacy_article_detail_culture",
                ],
            ),
            [
                ({"localid": "nonexistent"}, "legacy_journal:legacy_article_id"),
                (
                    {
                        "journal_code": "nonexistent",
                        "issue_localid": "nonexistent",
                        "localid": "nonexistent",
                        "format_identifier": "html",
                    },
                    "legacy_journal:legacy_article_detail_culture_localidentifier",
                ),
            ],
        ),
    )
    def article_url(self, request):
        kwargs = request.param[0]
        url = request.param[1]
        return reverse(url, kwargs=kwargs)

    def test_legacy_url_for_nonexistent_journals_404s(self, journal_url):
        response = Client().get(journal_url, follow=True)
        assert response.status_code == 404

    def test_legacy_url_for_nonexistent_issues_404s(self, issue_url):
        response = Client().get(issue_url, follow=True)
        assert response.status_code == 404

    def test_legacy_url_for_nonexistent_articles_404s(self, article_url):
        response = Client().get(article_url, follow=True)
        assert response.status_code == 404


class TestArticleXmlView:
    def test_can_retrieve_xml_of_existing_articles(self):
        journal = JournalFactory(open_access=True)
        issue = IssueFactory.create(
            journal=journal,
            year=2010,
            is_published=True,
            date_published=dt.datetime.now() - dt.timedelta(days=1000),
        )
        article = ArticleFactory.create(issue=issue)

        journal_id = issue.journal.localidentifier
        issue_id = issue.localidentifier
        article_id = article.localidentifier
        url = reverse(
            "public:journal:article_raw_xml",
            args=(journal_id, issue.volume_slug, issue_id, article_id),
        )
        response = Client().get(url)

        assert response.status_code == 200
        assert response["Content-Type"] == "application/xml"


class TestArticleMediaView:
    @pytest.mark.parametrize(
        "image, expected_content_type",
        (
            ("pixel.png", "image/png"),
            ("logo.jpg", "image/jpeg"),
        ),
    )
    def test_article_media_content_type(self, image, expected_content_type, monkeypatch):
        article = ArticleFactory()
        with open(os.path.join(FIXTURE_ROOT, image), "rb") as f:
            monkeypatch.setattr(
                ArticleMediaView,
                "get_datastream_content",
                unittest.mock.MagicMock(return_value=f.read()),
            )
        response = ArticleMediaView.as_view()(
            RequestFactory().get("/"),
            journal_code=article.issue.journal.code,
            issue_localid=article.issue.localidentifier,
            localid=article.localidentifier,
            media_localid="test",
        )
        assert response.status_code == 200
        assert response["Content-Type"] == expected_content_type


class TestExternalURLRedirectViews:
    def test_can_redirect_to_issue_external_url(self):
        issue = IssueFactory.create(
            date_published=dt.datetime.now(), external_url="http://www.erudit.org"
        )

        response = Client().get(
            reverse(
                "public:journal:issue_external_redirect",
                kwargs={"localidentifier": issue.localidentifier},
            )
        )
        assert response.status_code == 302

    def test_can_redirect_to_journal_external_url(self):
        journal = JournalFactory(code="journal1", external_url="http://www.erudit.org")
        response = Client().get(
            reverse("public:journal:journal_external_redirect", kwargs={"code": journal.code})
        )
        assert response.status_code == 302


@pytest.mark.parametrize("export_type", ["bib", "enw", "ris"])
def test_article_citation_doesnt_html_escape(export_type):
    # citations exports don't HTML-escape values (they're not HTML documents).
    # TODO: test authors name. Templates directly refer to `erudit_object` and we we don't have
    # a proper mechanism in the upcoming fake fedora API to fake values on the fly yet.
    title = "rock & rollin'"
    article = ArticleFactory.create(title=title)
    issue = article.issue
    url = reverse(
        "public:journal:article_citation_{}".format(export_type),
        kwargs={
            "journal_code": issue.journal.code,
            "issue_slug": issue.volume_slug,
            "issue_localid": issue.localidentifier,
            "localid": article.localidentifier,
        },
    )
    response = Client().get(url)
    content = response.content.decode()
    assert title in content


@pytest.mark.parametrize(
    "view_name",
    (
        "article_detail",
        "article_summary",
        "article_biblio",
        "article_toc",
    ),
)
def test_no_html_in_structured_data(view_name):
    article = ArticleFactory(
        from_fixture="038686ar",
        localidentifier="article",
        issue__localidentifier="issue",
        issue__year="2019",
        issue__journal__code="journal",
    )
    url = reverse(
        f"public:journal:{view_name}",
        kwargs={
            "journal_code": article.issue.journal.code,
            "issue_slug": article.issue.volume_slug,
            "issue_localid": article.issue.localidentifier,
            "localid": article.localidentifier,
        },
    )
    response = Client().get(url)
    content = response.content.decode()
    expected = (
        "{\n    "
        '"@type": "ListItem",\n    '
        '"position": 5,\n    '
        '"item": {\n      '
        '"@id": "http://example.com/fr/revues/journal/2019-issue/article/",\n      '
        '"name": "Constantin, François (dir.), Les biens publics mondiaux. '
        "Un mythe légitimateur pour l’action collective\xa0?, "
        'coll. Logiques politiques, Paris, L’Harmattan, 2002, 385\xa0p."\n    '
        "}\n  "
        "}"
    )
    assert expected in content
