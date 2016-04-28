# -*- coding: utf-8 -*-

from django.conf import settings
import pysolr

from core.solrq import Search as BaseSearch


# This is the object that will be used to query the Solr index.
client = pysolr.Solr(settings.SOLR_ROOT, timeout=10)


class Search(BaseSearch):
    filters_mapping = {
        'all': 'TexteComplet:{all}',
        'meta': 'Metadonnees:{meta}',
        'full_text': 'TexteIntegral:{full_text}',
        'title_abstract_keywords': 'TitreResumeMots:{title_abstract_keywords}',
        'title': 'Titre_idx:{title}',
        'author': 'Auteur_idx:{author}',
        'author_affiliation': 'Affiliation_idx:{author_affiliation}',
        'journal_title': 'TitreCollection_idx:{journal_title}',
        'bibliography': 'RefBiblio_idx:{bibliography}',
        'title_reviewd': 'TitreRefBiblio_idx:{title_reviewd}',
        'issn': 'ISSN:{issn}',
        'isbn': 'ISBN:{isbn}',
    }

    extra_params = {
        'rows': 1000000000,
        'fl': 'ID',
        'facet': 'true',
        'facet.field': [
            'AnneePublication',
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
    return Search(client)
