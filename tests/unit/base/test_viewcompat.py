import pytest
from django.test import Client

from erudit.fedora import repository
from erudit.test.factories import ArticleFactory
from erudit.test.factories import IssueFactory

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
