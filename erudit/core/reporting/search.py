# -*- coding: utf-8 -*-

from core.solrq import Search

from .client import client


class ReportingSearch(Search):
    filters_mapping = {
        'author': '(Auteur_tri:*{author}* OR Auteur_fac:*{author}*)',
        'collection': 'Fonds_fac:{collection}',
        'journal': '(RevueAbr:{journal} OR RevueID:{journal})',
        'type': 'Corpus_fac:{type}',
        'year': 'AnneePublication:{year}',
    }

    extra_params = {
        'rows': 0,
        'facet': 'true',
        'facet.field': [
            'RevueID',
            'NumeroID',
            'AnneePublication',
            'Auteur_tri',
            'Corpus_fac',
        ],
        'facet.sort': 'index',
    }


search = ReportingSearch(client)
