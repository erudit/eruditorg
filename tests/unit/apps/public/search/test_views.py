import pytest
import unittest

from bs4 import BeautifulSoup
from django.test import Client
from django.urls import reverse

from apps.public.journal.viewmixins import SolrDataMixin
from apps.public.search.forms import SearchForm
from erudit.test.factories import ArticleFactory, SolrDocumentFactory, ThesisFactory
from erudit.test.fedora import FakeAPI
from erudit.test.solr import FakeSolrData


@pytest.mark.django_db
class TestSearchResultsView:
    @pytest.fixture(autouse=True)
    def search_form_solr_data(self, monkeypatch):
        monkeypatch.setattr(SearchForm, "solr_data", FakeSolrData())

    def test_search_results_can_cite_thesis(self, solr_client):
        ThesisFactory()

        doc = SolrDocumentFactory(
            title="Thèse",
            type="Thèses",
            year="1999",
            language="fr",
        )
        solr_client.add_document(doc)
        url = reverse("public:search:results")
        response = Client().get(
            url,
            data={
                "basic_search_term": "*",
                "publication_types": "Thèses",
            },
        )
        html = response.content.decode()
        dom = BeautifulSoup(html, "html.parser")
        results = dom.find("ol", {"class": "results"})
        assert len(results.find_all("li", {"class": "result"})) == 1

    def test_search_results_citation_modal(self, solr_client):
        # Article in Fedora, citation tools should be not displayed, but we should have the URL to
        # get it with AJAX.
        ArticleFactory(
            localidentifier="foo",
            title="foo",
            issue__localidentifier="issue",
            issue__year="2021",
            issue__journal__code="journal",
        )
        # Search result not in Fedora, citation tools should not be displayed.
        doc = SolrDocumentFactory(id="bar", title="foo bar")
        solr_client.add_document(doc)

        url = reverse("public:search:results")
        response = Client().get(url, data={"basic_search_term": "foo"})
        html = response.content.decode()
        dom = BeautifulSoup(html, "html.parser")
        results = dom.find("ol", {"class": "results"})

        # There should be two search results.
        assert len(results.find_all("li", {"class": "result"})) == 2
        # The search result which is in fedora should display the citation tools.
        assert (
            results.find("a", {"id": "foo"}).attrs["href"]
            == "/fr/revues/journal/2021-issue/foo/ajax-citation-modal"
        )
        # The search result which is not in fedora should not display the citation tools.
        assert results.find("a", {"data-modal-id": "#id_cite_modal_bar"}) is None

    def test_search_results_citation_modal_is_the_same_as_the_article_detail(self, monkeypatch):
        monkeypatch.setattr(SolrDataMixin, "solr_data", FakeSolrData())

        article = ArticleFactory(localidentifier="foo", title="foo")

        # Search results citation modal window is populated with AJAX.
        url = reverse(
            "public:journal:article_ajax_citation_modal",
            kwargs={
                "journal_code": article.issue.journal.code,
                "issue_slug": article.issue.volume_slug,
                "issue_localid": article.issue.localidentifier,
                "localid": article.localidentifier,
            },
        )
        response = Client().get(url)
        html = response.content.decode()
        citation_modal = BeautifulSoup(html, "html.parser")

        url = reverse(
            "public:journal:article_detail",
            kwargs={
                "journal_code": article.issue.journal.code,
                "issue_slug": article.issue.volume_slug,
                "issue_localid": article.issue.localidentifier,
                "localid": article.localidentifier,
            },
        )
        response = Client().get(url, data={"basic_search_term": "foo"})
        html = response.content.decode()
        dom = BeautifulSoup(html, "html.parser")
        article_detail_citation_tools = dom.find("div", {"id": "id_cite_modal_foo"})

        assert article_detail_citation_tools in citation_modal

    def test_search_results_do_not_call_fedora(self):
        ArticleFactory(title="foo")
        with unittest.mock.patch("erudit.fedora.cache.requests") as mock_requests:
            fake_api = FakeAPI()
            mock_requests.get.side_effect = fake_api.get
            Client().get(reverse("public:search:results"), data={"basic_search_term": "foo"})
            assert mock_requests.get.call_count == 0
