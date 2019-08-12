from erudit.solr.models import SolrDocument


class TestSolrDocument:
    def test_localidentfier_doesnt_include_unb_prefix(self):
        assert SolrDocument({'ID': 'unb:123', 'Corpus_fac': 'Article'}).localidentifier == '123'
        assert SolrDocument({'ID': '123', 'Corpus_fac': 'Article'}).localidentifier == '123'
