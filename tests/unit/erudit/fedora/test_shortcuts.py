# -*- coding: utf-8 -*-

import unittest.mock

from erudit.fedora.shortcuts import get_cached_datastream_content
from erudit.test import BaseEruditTestCase


class TestGetCachedDatastreamContent(BaseEruditTestCase):
    def test_can_set_the_content_of_the_file_in_the_cache_if_it_is_not_there_already(self):
        # Setup
        mock_fedora_obj = unittest.mock.MagicMock()
        mock_fedora_obj.dstream = unittest.mock.MagicMock()
        mock_fedora_obj.dstream.content = 'dummy'
        mock_cache = unittest.mock.MagicMock()
        mock_cache_get = unittest.mock.MagicMock()
        mock_cache_get.return_value = None
        mock_cache_set = unittest.mock.MagicMock()
        mock_cache.get = mock_cache_get
        mock_cache.set = mock_cache_set
        # Run & check
        get_cached_datastream_content(mock_fedora_obj, 'dstream', cache=mock_cache)
        self.assertEqual(mock_cache_get.call_count, 1)
        self.assertEqual(mock_cache_set.call_count, 1)

    def test_can_use_the_content_of_the_file_in_the_cache_if_applicable(self):
        # Setup
        mock_fedora_obj = unittest.mock.MagicMock()
        mock_fedora_obj.dstream = unittest.mock.MagicMock()
        mock_fedora_obj.dstream.content = 'dummy'
        mock_cache = unittest.mock.MagicMock()
        mock_cache_get = unittest.mock.MagicMock()
        mock_cache_get.return_value = 'dummy'
        mock_cache_set = unittest.mock.MagicMock()
        mock_cache.get = mock_cache_get
        mock_cache.set = mock_cache_set
        # Run & check
        get_cached_datastream_content(mock_fedora_obj, 'dstream', cache=mock_cache)
        self.assertEqual(mock_cache_get.call_count, 1)
        self.assertEqual(mock_cache_set.call_count, 0)
