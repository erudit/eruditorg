from typing import (
    Dict,
    List,
    Tuple,
    Optional,
    cast,
)
from unittest import mock

import pytest
from django.test import Client
from django.urls import reverse

from apps.public.journal.views_compat import get_fedora_ids_from_url_kwargs
from apps.public.search.forms import SearchForm
from erudit.fedora import repository
from erudit.solr.models import SolrData
from erudit.test.factories import IssueFactory, ArticleFactory
from erudit.test.factories import JournalFactory

pytestmark = pytest.mark.django_db


def test_404s_for_unknown_urls():
    url = "/fr/test/unknown"
    response = Client().get(url)
    assert response.status_code == 404


@pytest.mark.parametrize(
    "url, expected_redirect_chain",
    [
        ("/these/", [("/fr/theses/", 301)]),
        ("/these/liste.html", [("/fr/theses/", 301)]),
        ("/these/index.html", [("/fr/theses/", 301)]),
        ("/client/login.jsp", [("/fr/compte/connexion/", 301)]),
        ("/client/getNewPassword.jsp", [("/fr/compte/mot-de-passe/reinitialisation/", 301)]),
        (
            "/client/updatePassword.jsp",
            [
                ("/fr/compte/mot-de-passe/", 301),
                ("/fr/compte/connexion/?next=/fr/compte/mot-de-passe/", 302),
            ],
        ),
        ("/recherche/index.html", [("/fr/recherche/avancee/", 301)]),
        ("/rss.xml", [("/fr/rss.xml", 301)]),
        ("/fr/index.html", [("/fr/", 301)]),
        ("/fr/revue/", [("/fr/revues/", 301)]),
        ("/fr/revue/index.html", [("/fr/revues/", 301)]),
        ("/fr/culture/", [("/fr/revues/", 301)]),
        ("/fr/culture/index.html", [("/fr/revues/", 301)]),
        ("/fr/abonnement/login.jsp", [("/fr/compte/connexion/", 301)]),
        (
            "/fr/abonnement/oublierPassword.jsp",
            [("/fr/compte/mot-de-passe/reinitialisation/", 301)],
        ),
        (
            "/fr/abonnement/modifierPassword.jsp",
            [
                ("/fr/compte/mot-de-passe/", 301),
                ("/fr/compte/connexion/?next=/fr/compte/mot-de-passe/", 302),
            ],
        ),
    ],
)
def test_legacy_urls_are_redirected_with_http_301(url, expected_redirect_chain, monkeypatch):
    monkeypatch.setattr(SearchForm, "solr_data", FakeSolrData(""))
    response = Client().get(url, follow=True)
    assert response.redirect_chain == expected_redirect_chain
    assert response.status_code == 200


def test_can_handle_legacy_journal_year_number_pattern():

    issue_1 = IssueFactory(number=1, volume=None, year=2000)
    IssueFactory(journal=issue_1.journal, number=1, volume=None, year=2001)

    legacy_url = "/revue/{journal_code}/{issue_year}/v/n{number}/index.html".format(
        journal_code=issue_1.journal.code, issue_year=issue_1.year, number=issue_1.number
    )

    assert Client().get(legacy_url).status_code == 301


def test_will_propagate_prepublication_ticket_received_in_querystring_for_issue():
    journal = JournalFactory(code="dummy")

    # Create a fake fedora issue for this journal
    issue_localidentifier = "{}.fake_publication".format(journal.pid)
    repository.api.register_publication(issue_localidentifier)

    legacy_url = "/revue/{journal_code}/1000/v1/n1/index.html".format(  # noqa
        journal_code=journal.code,
    )
    data = dict(id="fake_publication", ticket="ticket")

    resp = Client().get(legacy_url, data=data)
    assert "?ticket=ticket" in resp.url
    assert resp.status_code == 301


def test_will_propagate_prepublication_ticket_received_in_querystring_for_article():
    article = ArticleFactory(
        issue__volume="1", issue__number="1", issue__year=1000, issue__is_published=False
    )
    issue = article.issue  # type: Issue
    journal = issue.journal  # type: Journal

    legacy_url = "/revue/{journal_code}/1000/v1/n1/{article_localidentifier}.html".format(
        journal_code=journal.code, article_localidentifier=article.localidentifier
    )
    data = dict(id=issue.localidentifier, ticket=issue.prepublication_ticket)

    resp = Client().get(legacy_url, data=data, follow=True)
    url = resp.redirect_chain[-1][0]

    expected_url = reverse(
        "public:journal:article_detail",
        kwargs={
            "journal_code": journal.code,
            "issue_slug": issue.volume_slug,
            "issue_localid": issue.localidentifier,
            "localid": article.localidentifier,
        },
    )
    expected_url += "?ticket={}".format(issue.prepublication_ticket)
    assert expected_url == url
    assert resp.status_code == 200


class FakeSolrData:
    def __init__(self, fedora_ids):
        self.fedora_ids = fedora_ids

    # noinspection PyUnusedLocal
    def get_fedora_ids(self, localidentifier: str) -> Optional[Tuple[str, str, str]]:
        return self.fedora_ids

    # noinspection PyUnusedLocal
    def get_search_form_facets(self) -> Dict[str, List[Tuple[str, str]]]:
        return {
            "disciplines": [],
            "languages": [],
            "journals": [],
        }


@pytest.mark.django_db
class TestGetArticleFromUrlKwargs:
    def test_returns_none_when_no_localid(self):
        solr_data = cast(SolrData, FakeSolrData(("jc_solr", "issue_id", "article_id")))
        assert get_fedora_ids_from_url_kwargs(solr_data, {}) is None

    def test_returns_ids_when_issue_id_provided(self):
        solr_data = cast(SolrData, FakeSolrData(("jc_solr", "issue_id", "article_id")))
        fedora_ids = get_fedora_ids_from_url_kwargs(
            solr_data, {"journal_code": "jc", "issue_localid": "issue_id", "localid": "article_id"}
        )
        assert fedora_ids == ("jc", "issue_id", "article_id")

    def test_returns_none_when_no_issue_for_year_volume_number(self):
        solr_data = cast(SolrData, FakeSolrData(None))
        with mock.patch("apps.public.journal.views_compat.get_pids") as mock_get_pids:
            mock_get_pids.return_value = []
            fedora_ids = get_fedora_ids_from_url_kwargs(
                solr_data,
                {
                    "journal_code": "jc",
                    "year": "2018",
                    "v": "2",
                    "issue_number": "1",
                    "localid": "article_id",
                },
            )
            # since we do not find the issue in the db, and it's not in fake solr
            # nor in fake fedora, the funciton should return none
            assert fedora_ids is None

    def test_returns_ids_when_issue_found_for_year_volume_number(self):
        solr_data = cast(SolrData, FakeSolrData(("jc_solr", "issue_id", "article_id")))
        journal = JournalFactory(code="jc")
        IssueFactory(
            journal=journal, year="2018", volume="2", number="1", localidentifier="issue_id"
        )
        fedora_ids = get_fedora_ids_from_url_kwargs(
            solr_data,
            {
                "journal_code": "jc",
                "year": "2018",
                "v": "2",
                "issue_number": "1",
                "localid": "article_id",
            },
        )
        assert fedora_ids == ("jc", "issue_id", "article_id")

    def test_returns_ids_when_found_in_solr(self):
        solr_data = cast(SolrData, FakeSolrData(("jc_solr", "issue_id", "article_id")))
        fedora_ids = get_fedora_ids_from_url_kwargs(solr_data, {"localid": "article_id"})
        assert fedora_ids == ("jc_solr", "issue_id", "article_id")

    def test_returns_ids_when_not_found_in_solr_but_found_in_fedora(self):
        solr_data = cast(SolrData, FakeSolrData(None))
        with mock.patch("apps.public.journal.views_compat.get_pids") as mock_get_pids:
            mock_get_pids.return_value = ["erudit:erudit.jc.issueid.000666ar"]
            fedora_ids = get_fedora_ids_from_url_kwargs(solr_data, {"localid": "000666ar"})
            assert fedora_ids == ("jc", "issueid", "000666ar")
