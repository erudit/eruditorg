# -*- coding: utf-8 -*-

from erudit.test import BaseEruditTestCase
from erudit.test.factories import ArticleFactory


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
