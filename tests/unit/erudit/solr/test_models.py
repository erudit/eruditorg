import pysolr

from erudit.solr.models import (
    SolrDocument,
    get_all_solr_results,
)


class TestSolrDocument:
    def test_localidentfier_doesnt_include_unb_prefix(self):
        assert SolrDocument({"ID": "unb:123", "Corpus_fac": "Article"}).localidentifier == "123"
        assert SolrDocument({"ID": "123", "Corpus_fac": "Article"}).localidentifier == "123"


def test_get_all_solr_results():
    def make_results(results_docs):
        return pysolr.Results({"response": {"docs": results_docs}})

    results = [
        make_results([{"ID": "1"}, {"ID": "2"}]),
        make_results([{"ID": "3"}]),
        make_results([]),
    ]
    results_iterator = iter(results)

    start_rows = []

    def fake_search_function(**kwargs):
        start_rows.append(kwargs['start'])
        return next(results_iterator)

    docs = get_all_solr_results(fake_search_function, 2)
    assert docs == results[0].docs + results[1].docs
    assert start_rows == [0, 2, 4]
