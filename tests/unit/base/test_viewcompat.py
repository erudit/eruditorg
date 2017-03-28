# -*- coding: utf-8 -*-

from erudit.test import BaseEruditTestCase
from erudit.test.factories import ArticleFactory
from erudit.test.factories import IssueFactory


class TestCanRedirectToRetro(BaseEruditTestCase):
    def test_can_redirect_to_retro_for_unknown_urls(self):
        # Setup
        url = '/fr/test/unknown'
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 301)

    def test_legacy_urls_return_are_redirected_with_http_301(self):
        article = ArticleFactory()

        legacy_urls = [
            "/recherche/index.html",
            "/client/login.jsp",
            "/client/login.jsp?lang=en",
            "/these/liste.html",
            "/rss.xml",

        ]

        for url in legacy_urls:
            assert self.client.get(url).status_code == 301

    def test_can_handle_legacy_journal_year_number_pattern(self):

        issue_1 = IssueFactory(number=1, volume=None, year=2000)
        issue_2 = IssueFactory(journal=issue_1.journal, number=1, volume=None, year=2001)

        legacy_url = "/revue/{journal_code}/{issue_year}/v/n{number}/index.html".format(
            journal_code=issue_1.journal.code,
            issue_year=issue_1.year,
            number=issue_1.number
        )

        assert self.client.get(legacy_url).status_code == 301
