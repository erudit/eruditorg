import erudit.solr.models
from core.solrq import Search as BaseSearch


class Search(BaseSearch):
    filters_mapping = {
        'all': 'TexteComplet:({all})',
        'meta': 'Metadonnees:({meta})',
        'full_text': 'TexteIntegral:({full_text})',
        'title_abstract_keywords': 'TitreResumeMotsCles_idx:({title_abstract_keywords})',
        'title': 'Titre_idx:({title})',
        'author': 'Auteur_idx:({author})',
        'author_affiliation': 'Affiliation_idx:({author_affiliation})',
        'journal_title': 'TitreCollection_idx:({journal_title})',
        'bibliography': 'RefBiblio_idx:({bibliography})',
        'title_reviewd': 'TitreRefBiblio_idx:({title_reviewd})',
        'issn': 'ISSN:({issn})',
        'isbn': 'ISBN:({isbn})',
    }

    extra_params = {
        'rows': 10,
        'facet': 'true',
        'defType': 'edismax',
        'facet.field': [
            'Annee',
            'TypeArticle_fac',
            'Langue',
            'TitreCollection_fac',
            'Auteur_tri',
            'Fonds_fac',
            'Corpus_fac',
        ],
    }


def get_search():
    """ Returns a search object allowing to perform queries. """
    return Search(erudit.solr.models.client)
