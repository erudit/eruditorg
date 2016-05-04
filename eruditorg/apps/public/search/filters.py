# -*- coding: utf-8 -*-

from elasticsearch_dsl import A
from elasticsearch_dsl import Q
from elasticsearch_dsl import Search

from erudit.index import get_client
from erudit.index.conf import settings as index_settings

from .conf import settings as search_settings


class EruditDocumentElasticsearchFilter(object):
    """ Filter that returns a list of EruditDocument instance based on Elasticsearch search results.

    This "filter" class can process many individual filters that should be translated to
    Elasticsearch parameters in order to query an Elasticsearch index of Érudit documents. This
    filter should only be used on API views associated with EruditDocument-related models.
    """
    OP_AND = 'AND'
    OP_OR = 'OR'
    OP_NOT = 'NOT'
    operators = [OP_AND, OP_OR, OP_NOT, ]

    def build_es_filters(self, query_params={}):
        """ Return the filters to use to query the Elasticsearch index. """
        filters = {}

        # Simple search parameters
        basic_search_term = query_params.get('basic_search_term', '*')
        basic_search_field = query_params.get('basic_search_field', 'all')
        basic_search_operator = query_params.get('basic_search_operator', None)
        filters.update({'q': {
            'term': basic_search_term, 'field': basic_search_field,
            'operator': self.OP_NOT if basic_search_operator is not None else None}})

        # Advanced search parameters
        advanced_q = []
        for i in range(search_settings.MAX_ADVANCED_PARAMETERS):
            search_term = query_params.get('advanced_search_term{}'.format(i + 1), None)
            search_field = query_params.get('advanced_search_field{}'.format(i + 1), 'all')
            search_operator = query_params.get('advanced_search_operator{}'.format(i + 1), None)

            if search_term and search_operator in self.operators:
                advanced_q.append({
                    'term': search_term, 'field': search_field, 'operator': search_operator, })
        filters.update({'advanced_q': advanced_q})

        # Publication year filters
        pub_years = query_params.getlist('years', [])
        pub_year_start = query_params.get('pub_year_start', None)
        pub_year_end = query_params.get('pub_year_end', None)
        if pub_years:
            filters.update({'pub_years': pub_years})
        if pub_year_start:
            filters.update({'pub_year_start': pub_year_start})
        if pub_year_end:
            filters.update({'pub_year_end': pub_year_end})

        # Types of documents filter
        document_types = query_params.getlist('article_types', [])
        if document_types:
            filters.update({'document_types': document_types})

        # Languages filter
        languages = query_params.getlist('languages', [])
        if languages:
            filters.update({'languages': languages})

        # Collections/journals filter
        journals = query_params.getlist('collections', [])
        if journals:
            filters.update({'journals': journals})

        # Authors filter
        authors = query_params.getlist('authors', [])
        if authors:
            filters.update({'authors': authors})

        # Funds filter
        funds = query_params.getlist('funds', [])
        if funds:
            filters.update({'funds': funds})

        # Publication types filter
        publication_types = query_params.getlist('publication_types', [])
        if publication_types:
            filters.update({'publication_types': publication_types})

        return filters

    def apply_es_filters(self, filters):
        """ Applies the solr filters and returns the list of results. """
        search = Search(using=get_client(), index=index_settings.ES_INDEX_NAME)

        qfield = filters['q']['field']
        qterm = filters['q']['term']
        qoperator = filters['q']['operator']
        advanced_q = filters.get('advanced_q', [])

        pub_years = filters.get('pub_years', [])
        pub_year_start = filters.get('pub_year_start', None)
        pub_year_end = filters.get('pub_year_end', None)

        document_types = filters.get('document_types', [])

        languages = filters.get('languages', [])

        journals = filters.get('journals', [])

        authors = filters.get('authors', [])

        funds = filters.get('funds', [])

        publication_types = filters.get('publication_types', [])

        # Main filters
        query = Q('term', **{qfield: qterm}) if qoperator is None or qoperator != self.OP_NOT \
            else ~Q('term', **{qfield: qterm})
        for qparams in advanced_q:
            term = qparams.get('term')
            field = qparams.get('field')
            operator = qparams.get('operator')
            if operator == self.OP_AND:
                query &= Q('term', **{field: term})
            elif operator == self.OP_OR:
                query |= Q('term', **{field: term})
            elif operator == self.OP_NOT:
                query &= ~Q('term', **{field: term})
        sqs = search.query('bool', filter=[query])

        # Applies the publication year filters
        if pub_year_start or pub_year_end:
            ystart = pub_year_start if pub_year_start is not None else '*'
            yend = pub_year_end if pub_year_end is not None else '*'
            sqs = sqs.query('range', publication_year={'gte': ystart, 'lte': yend})
        elif pub_years:
            sqs = sqs.filter('terms', publication_year=pub_years)

        # Applies the types of documents filter
        if document_types:
            sqs = sqs.filter('terms', article_type=document_types)

        # Applies the languages filter
        if languages:
            sqs = sqs.filter('terms', lang=languages)

        # Applies the journals filter
        if journals:
            sqs = sqs.filter('terms', **{'collection.raw': journals})

        # Applies the authors filter
        if authors:
            sqs = sqs.filter('terms', **{'authors.raw': authors})

        return sqs

    def apply_es_sorting(self, es_query, query_params={}):
        """ Sorts the list of results. """
        sort = query_params.get('sort_by', 'relevance')
        if sort == 'relevance':
            return es_query
        elif sort == 'title_asc':
            return es_query.sort('title.sort')
        elif sort == 'title_desc':
            return es_query.sort('-title.sort')
        elif sort == 'author_asc':
            return es_query.sort({'authors.sort': {'order': 'asc', 'mode': 'min'}})
        elif sort == 'author_desc':
            return es_query.sort({'authors.sort': {'order': 'desc', 'mode': 'min'}})
        elif sort == 'pubdate_asc':
            return es_query.sort('publication_date')
        elif sort == 'pubdate_desc':
            return es_query.sort('-publication_date')

    def filter(self, request, queryset, view):
        """ Filters the queryset by using the results provided by the Elasticsearch index. """
        params = request.query_params.copy()

        # Firt we have to retrieve all the considered Elasticsearch filters
        filters = self.build_es_filters(params)

        # Then apply the filters in order to get lazy query containing all the filters
        es_query = self.apply_es_filters(filters)

        # Apply sorting
        es_query = self.apply_es_sorting(es_query, params)

        # Prepares aggregations
        es_query.aggs.bucket('year', A('terms', field='publication_year'))
        es_query.aggs.bucket('article_type', A('terms', field='article_type'))
        es_query.aggs.bucket('language', A('terms', field='lang'))
        es_query.aggs.bucket('collection', A('terms', field='collection.raw'))
        es_query.aggs.bucket('author', A('terms', field='authors.raw'))

        # Prepares the values used to paginate the results using Elasticsearch.
        page_size = request.query_params.get('page_size', search_settings.DEFAULT_PAGE_SIZE)
        page = request.query_params.get('page', 1)
        try:
            start = (int(page) - 1) * int(page_size)
            end = int(page_size)
        except ValueError:  # pragma: no cover
            start = 0

        # Trigger the execution of the query in order to get a list of results from the
        # Elasticsearch index. Here we use "fields([])" in order to remove document sources from the
        # returned results.
        result = es_query.fields([])[start:end].execute()

        # Determines the localidentifiers of the documents in order to filter the queryset
        localidentifiers = [r.meta['id'] for r in result.hits]

        # Prepares the dictionnary containing aggregation results.
        aggregations_dict = {}
        for agg in result.aggregations:
            fdict = {b['key']: b['doc_count'] for b in result.aggregations[agg]['buckets']}
            aggregations_dict.update({agg: fdict})

        return es_query.count(), localidentifiers, aggregations_dict
