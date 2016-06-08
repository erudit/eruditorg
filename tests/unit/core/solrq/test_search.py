# -*- coding: utf-8 -*-

import json
import unittest.mock

from pysolr import Results
from pysolr import Solr

from core.solrq.query import Query
from core.solrq.search import Search
from core.solrq.test import FIXTURE_ROOT
from core.solrq.test import SolrqTestCase


class TestSearch(SolrqTestCase):
    def test_can_return_a_query_instance_when_performing_filters(self):
        # Setup
        search = Search(self.client)
        # Run
        q = search.filter()
        # Check
        self.assertTrue(isinstance(q, Query))

    @unittest.mock.patch.object(Solr, 'search')
    def test_can_return_results(self, mock_search):
        # Setup
        with open(FIXTURE_ROOT + '/response1.solr.json', mode='r') as fp:
            json_content = fp.read()
        decoded = json.loads(json_content)
        mock_search.return_value = Results(decoded)
        search = Search(self.client)
        # Run
        results = search.results
        # Check
        self.assertTrue(isinstance(results, Results))
        self.assertEqual(results.hits, 1)
