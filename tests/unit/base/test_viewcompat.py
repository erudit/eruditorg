import pytest
from django.test import Client

from erudit.fedora import repository
from erudit.test.factories import ArticleFactory
from erudit.test.factories import IssueFactory
from erudit.test.factories import JournalFactory

pytestmark = pytest.mark.django_db


def test_can_redirect_to_retro_for_unknown_urls():
    url = '/fr/test/unknown'
    response = Client().get(url)
    assert response.status_code == 301


@pytest.mark.django_db
class TestCanRedirectToRetro:


    def test_can_redirect_to_retro_for_unknown_urls(self):
        # Setup
        url = '/fr/test/unknown'
        # Run
        response = Client().get(url)
        # Check
        assert response.status_code == 301

    @pytest.mark.parametrize('url', [
        "/recherche/index.html",
        "/client/login.jsp",
        "/client/login.jsp?lang=en",
        "/these/liste.html",
        "/rss.xml",
    ])
    def test_legacy_urls_return_are_redirected_with_http_301(self, url):
        assert Client().get(url).status_code == 301


def test_can_handle_legacy_journal_year_number_pattern():

    issue_1 = IssueFactory(number=1, volume=None, year=2000)
    IssueFactory(journal=issue_1.journal, number=1, volume=None, year=2001)

    legacy_url = "/revue/{journal_code}/{issue_year}/v/n{number}/index.html".format(
        journal_code=issue_1.journal.code,
        issue_year=issue_1.year,
        number=issue_1.number
    )

    assert Client().get(legacy_url).status_code == 301


def test_will_propagate_prepublication_ticket_received_in_querystring():
    journal = JournalFactory(code="dummy")

    # Create a fake fedora issue for this journal
    issue_localidentifier = "{}.fake_publication".format(journal.pid)
    repository.api.register_publication(issue_localidentifier)


    legacy_url = "/revue/{journal_code}/1000/v1/n1/index.html".format(  # noqa
        journal_code=journal.code,
    )
    data = dict(
        id="fake_publication",
        ticket="ticket"
    )

    resp = Client().get(legacy_url, data=data)
    assert "?ticket=ticket" in resp.url
    assert resp.status_code == 301
