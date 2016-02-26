# -*- coding: utf-8 -*-

from .solr_search import search as default_search


class ReportingQuery(object):
    """
    The ReportingQuery class can be used as a convenient way to filter
    information on the Érudit Solr index.
    """
    filter_query_config = {
        'journal': '(RevueAbr:{journal} OR RevueID:{journal})',
        'author': '(Auteur_tri:*{author}* OR Auteur_fac:*{author}*)',
        'year': 'AnneePublication:{year}',
    }

    def __init__(self, search=None, qs='*:*'):
        self.search = default_search if search is None else search
        self._qs = qs

    def filter(self, op='AND', **kwargs):
        """ Prepares the querystring used to perform a query.

        This method returns a new instance of ReportingQuery that allows
        to add another filters to the initial querystring.
        """
        qs = self._qs
        for k, v in kwargs.items():
            if k in self.filter_query_config:
                subqs = self.filter_query_config[k].format(**{k: v})
            else:
                subqs = '{0}:{1}'.format(k, v)
            qs = ' {} '.format(op).join([qs, subqs])

        return self.__class__(self.search, qs)

    def get_results(self):
        """ Triggers the search and returns the results. """
        return default_search.search(self._qs, **{
            'rows': 1000000000,
            'facet': 'true',
            'facet.field': ['NumeroID', 'AnneePublication', 'Auteur_tri', ],
        })

    results = property(get_results)
