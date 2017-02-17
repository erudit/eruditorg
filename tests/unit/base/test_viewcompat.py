# -*- coding: utf-8 -*-

from erudit.test import BaseEruditTestCase


class TestCanRedirectToRetro(BaseEruditTestCase):
    def test_can_redirect_to_retro_for_unknown_urls(self):
        # Setup
        url = '/fr/test/unknown'
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 301)
