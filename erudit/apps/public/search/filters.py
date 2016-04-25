# -*- coding: utf-8 -*-

from rest_framework import filters

from core.solrq.query import Q

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
        basic_search_operator = query_params.get('basic_search_operator', None)
        filters.update({'q': {
            'term': basic_search_term, 'field': basic_search_field,
            'operator': basic_search_operator}})

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

    def apply_solr_filters(self, filters):
        """ Applies the solr filters and returns the list of results. """
        search = solr_search.get_search()

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
        query = Q(**{qfield: qterm}) if qoperator is None or qoperator != self.OP_NOT \
            else ~Q(**{qfield: qterm})
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

        # Applies the publication year filters
        if pub_year_start or pub_year_end:
            ystart = pub_year_start if pub_year_start is not None else '*'
            yend = pub_year_end if pub_year_end is not None else '*'
            sqs = sqs.filter(AnneePublication='[{start} TO {end}]'.format(start=ystart, end=yend))
        elif pub_years:
            sqs = self._filter_solr_multiple(sqs, 'AnneePublication', pub_years)

        # Applies the types of documents filter
        if document_types:
            sqs = self._filter_solr_multiple(sqs, 'TypeArticle_fac', document_types)

        # Applies the languages filter
        if languages:
            sqs = self._filter_solr_multiple(sqs, 'Langue', languages)

        # Applies the journals filter
        if journals:
            sqs = self._filter_solr_multiple(sqs, 'TitreCollection_fac', journals)

        # Applies the authors filter
        if authors:
            sqs = self._filter_solr_multiple(sqs, 'Auteur_tri', authors)

        # Applies the funds filter
        if funds:
            sqs = self._filter_solr_multiple(sqs, 'Fonds_fac', funds)

        # Applies the publication types filter
        if publication_types:
            sqs = self._filter_solr_multiple(sqs, 'Corpus_fac', publication_types)

        return sqs

    def get_solr_sorting(self, request):
        """ Get the Solr sorting string. """
        sort = request.query_params.get('sort', 'relevance')
        if sort == 'relevance':
            return 'score desc'
        elif sort == 'title_asc':
            return 'Titre_tri asc'
        elif sort == 'title_desc':
            return 'Titre_tri desc'
        elif sort == 'author_asc':
            return 'Auteur_tri asc'
        elif sort == 'author_desc':
            return 'Auteur_tri desc'

    def filter_queryset(self, request, queryset, view):
        """ Filters the queryset by using the results provided by the Solr index. """
        # Firt we have to retrieve all the considered Solr filters
        filters = self.build_solr_filters(request.query_params.copy())

        # Then apply the filters in order to get lazy query containing all the filters
        solr_query = self.apply_solr_filters(filters)

        # Trigger the execution of the query in order to get a list of results from the Solr index
        results = solr_query.get_results(sort=self.get_solr_sorting(request))

        # Determines the localidentifiers of the documents in order to filter the queryset
        localidentifiers = [r['ID'] for r in results.docs]

        # Determines the localidentifiers that are present in the database by keeping the order of
        # the filtered results. We convert the list of localidentifiers returned from the DB to a
        # set because checking for membership in a set or similar hash-based type is roughly O(1),
        # compared to O(n) for membership in a list.
        db_localidentifiers = queryset.values_list('localidentifier', flat=True)
        db_filtered_localidentifiers = [
            lid for lid in localidentifiers if lid in frozenset(db_localidentifiers)]

        # Note: we could've filtered the queryset using the list of localidentifiers. However this
        # filter is aimed to be used along with the EruditDocumentPagination whic paginates the
        # objects using the list of localidentifiers. So the objects are filtered at pagination-time
        # anyway.

        return db_filtered_localidentifiers, queryset

    def _filter_solr_multiple(self, sqs, field, values):
        query = Q()
        for v in values:
            query |= Q(**{field: '"{}"'.format(v)})
        return sqs.filter(query)
