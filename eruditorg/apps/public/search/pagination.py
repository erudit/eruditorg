# -*- coding:utf-8 -*-

import itertools
from functools import reduce

from django.core.paginator import InvalidPage
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .conf import settings as search_settings
from .models import get_type_for_corpus, GenericSolrDocument


class EruditDocumentPagination(PageNumberPagination):
    page_size = search_settings.DEFAULT_PAGE_SIZE
    page_size_query_param = 'page_size'
    max_page_size = 50

    in_database_corpus = ('Article', 'Culturel', 'Thèses')

    def get_paginated_response(self, data):
        return Response({
            'pagination': {
                'count': self.page.paginator.count,
                'num_pages': self.page.paginator.num_pages,
                'current_page': self.page.number,
                'next_page': self.page.next_page_number() if self.page.has_next() else None,
                'previous_page': (
                    self.page.previous_page_number()if self.page.has_previous() else None),
                'page_size': self.page.paginator.per_page,
                'links': {
                    'next': self.get_next_link(),
                    'previous': self.get_previous_link(),
                },
            },
            'results': data,
        })

    def _group_by_external_document(self, documents):
        """ Helper method to group documents by internal or external

        :returns: a tuple of iterators (internal_documents, external_documents)
        """
        def test_func(obj):
            return obj['Corpus_fac'] in self.in_database_corpus
        internal_documents = filter(test_func, documents)
        external_documents = itertools.filterfalse(test_func, documents)
        return internal_documents, external_documents

    def paginate(self, docs_count, documents, queryset, request, view=None):
        """
        This is the default implementation of the PageNumberPagination.paginate_queryset method ;
        the only exception: the pagination is performed on a dummy list of the same length as the
        number of results returned by the search engine in use. But the EruditDocument instances
        corresponding to the documents associated with the current page are returned. Note
        that these documents have already been paginated by the search engine.
        """
        page_size = self.get_page_size(request)
        if not page_size:  # pragma: no cover
            return None

        paginator = self.django_paginator_class(range(docs_count), page_size)
        page_number = request.query_params.get(self.page_query_param, 1)
        if page_number in self.last_page_strings:  # pragma: no cover
            page_number = paginator.num_pages

        try:
            self.page = paginator.page(page_number)
        except InvalidPage:  # pragma: no cover
            msg = self.invalid_page_message.format(page_number=page_number)
            raise NotFound(msg)

        if paginator.num_pages > 1 and self.template is not None:  # pragma: no cover
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request

        # This is a specific case in order to remove some sub-strings from the localidentifiers
        # at hand. This is a bit ugly but we are limited here by the predefined Solr document IDs.
        # For example the IDs are prefixed by "unb:" for UNB articles... But UNB localidentifiers
        # should not be stored with "unb:" into the database.
        drop_keywords = ['unb:', ]
        for document in documents:
            document['ID'] = reduce(lambda s, k: s.replace(k, ''), drop_keywords, document['ID'])

        # Split by internal and external documents
        # internal documents are documents that we fully support on the platform
        # external documents are documents that need to be displayed on an external website (retro)
        internal_documents, external_documents = self._group_by_external_document(documents)
        external_documents_dict = {d['ID']: d for d in external_documents}

        # Retrieve the documents from the database
        localidentifiers = [d['ID'] for d in documents]
        queryset = queryset.filter(localidentifier__in=localidentifiers)
        obj_dict = {obj.localidentifier: obj for obj in queryset}

        obj_list = []
        for d in documents:
            obj = None
            if d['ID'] in obj_dict:
                obj = obj_dict[d['ID']]

            elif not d['Corpus_fac'] in self.in_database_corpus:
                obj = get_type_for_corpus(d['Corpus_fac'])(
                    localidentifier=d['ID'],
                    data=external_documents_dict[d['ID']]
                )
            if obj:
                obj_list.append(obj)
            else:
                obj_list.append(
                    GenericSolrDocument(
                        localidentifier=d['ID'],
                        data=d
                    )
                )

        return obj_list
