import json

from pysolr import Results

from core.solrq.query import Query
from core.solrq.search import Search
from core.solrq.test import FIXTURE_ROOT


class TestSearch:
    def test_can_return_a_query_instance_when_performing_filters(self, solr_client):
        # Setup
        search = Search(solr_client)
        # Run
        q = search.filter()
        # Check
        assert isinstance(q, Query)

    def test_can_return_results(self, solr_client):
        with open(FIXTURE_ROOT + "/response1.solr.json", mode="r") as fp:
            json_content = fp.read()
        decoded = json.loads(json_content)
        solr_client.search = lambda *a, **kw: Results(decoded)
        search = Search(solr_client)
        results = search.results
        assert isinstance(results, Results)
        assert results.hits == 1
