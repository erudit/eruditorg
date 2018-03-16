import pytest

from eruditorg.apps.public.search.serializers import GenericSolrDocumentSerializer


def _get_GenericSolrDocument():
    return {
        'ID': 'abc123',
        'URLDocument': ['http://example.com'],
        'Titre_fr': 'titre',
        'Corpus_fac': 'whatever',
    }


def test_GenericSolrDocumentSerializer():
    doc = _get_GenericSolrDocument()
    ser = GenericSolrDocumentSerializer(doc).data
    assert ser['url'] == 'http://example.com'
    assert ser['title'] == 'titre'


@pytest.mark.parametrize(
    'titleattr',
    {'Titre_en', 'TitreRefBiblio_aff'})
def test_GenericSolrDocumentSerializer_title_attrs(titleattr):
    # Test that we support alternative title attrs
    doc = _get_GenericSolrDocument()
    del doc['Titre_fr']
    doc[titleattr] = 'autretitre'
    ser = GenericSolrDocumentSerializer(doc).data
    assert ser['title'] == 'autretitre'


def test_GenericSolrDocumentSerializer_unknown_title_attr():
    # When we have a document with no known title attr, we have a "Sans titre" fallback title
    # (instead of "None")
    doc = _get_GenericSolrDocument()
    del doc['Titre_fr']
    ser = GenericSolrDocumentSerializer(doc).data
    assert isinstance(ser['title'], str)
