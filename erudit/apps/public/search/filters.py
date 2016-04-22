# -*- coding: utf-8 -*-

import django_filters
from rest_framework import filters

from core.solrq.query import Q
from erudit.models import EruditDocument

from . import solr_search


class EruditDocumentSolrFilter(filters.BaseFilterBackend):
    """ Filter that returns a list of EruditDocument instance based on Solr search results.

    This "filter" class can process many individual filters that should be translated to Solr
    parameters in order to query a Solr index of Érudit documents. This filter should only be used
    on API views associated with EruditDocument-related models.
    """
    max_advanced_search_parameters = 10

    OP_AND = 'AND'
    OP_OR = 'OR'
    OP_NOT = 'NOT'
    operators = [OP_AND, OP_OR, OP_NOT, ]

    def build_solr_filters(self, query_params={}):
        """ Return the filters to use to query the Solr index. """
        filters = {}

        # Simple search parameters
        basic_search_term = query_params.get('basic_search_term', '*')
        basic_search_field = query_params.get('basic_search_field', 'all')
        filters.update({'q': {'term': basic_search_term, 'field': basic_search_field, }})

        # Advanced search parameters
        advanced_q = []
        for i in range(self.max_advanced_search_parameters):
            search_term = query_params.get('advanced_search_term{}'.format(i + 1), None)
            search_field = query_params.get('advanced_search_field{}'.format(i + 1), 'all')
            search_operator = query_params.get('advanced_search_operator{}'.format(i + 1), None)

            if search_term and search_operator in self.operators:
                advanced_q.append({
                    'term': search_term, 'field': search_field, 'operator': search_operator, })
        filters.update({'advanced_q': advanced_q})

        return filters

    def apply_solr_filters(self, filters):
        """ Applies the solr filters and returns the list of results. """
        search = solr_search.get_search()
        qfield = filters['q']['field']
        qterm = filters['q']['term']
        advanced_q = filters.get('advanced_q', [])

        # Main filters
        query = Q(**{qfield: qterm})
        for qparams in advanced_q:
            term = qparams.get('term')
            field = qparams.get('field')
            operator = qparams.get('operator')
            if operator == self.OP_AND:
                query &= Q(**{field: term})
            elif operator == self.OP_OR:
                query |= Q(**{field: term})
            elif operator == self.OP_NOT:
                query &= ~Q(**{field: term})

        sqs = search.filter(query)

        return sqs.get_results()

    def filter_queryset(self, request, queryset, view):
        """ Filters the queryset by using the results provided by the Solr index. """
        # Firt we have to retrieve all the considered Solr filters
        filters = self.build_solr_filters(request.query_params.copy())

        # Then apply the filters in order to get a list of results from the Solr index
        results = self.apply_solr_filters(filters)

        # Determines the localidentifiers of the documents in order to filter the queryset
        localidentifiers = [r['ID'] for r in results.docs]

        return queryset.filter(localidentifier__in=localidentifiers)


class _EruditDocumentSolrFilter(django_filters.FilterSet):
    q = django_filters.MethodFilter(action='filter_by_q', distinct=True)

    class Meta:
        model = EruditDocument

    def __init__(self, *args, **kwargs):
        super(_EruditDocumentSolrFilter, self).__init__(*args, **kwargs)
        self.solr_search = solr_search.get_search()

    def filter_by_q(self, queryset, value):
        return queryset

    @property
    def qs(self):
        print(self.filters)
        qs = super(_EruditDocumentSolrFilter, self).qs
        print("O")
        return qs
