# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property

from erudit.models import Author
from erudit.models import SearchUnitCollection
from erudit.models import SearchUnitDocument


class SearchUnitDetailMixin(object):
    def get_search_unit(self):
        raise NotImplementedError

    @cached_property
    def search_unit(self):
        return self.get_search_unit()


class SearchUnitStatsMixin(SearchUnitDetailMixin):
    def get_context_data(self, **kwargs):
        context = super(SearchUnitStatsMixin, self).get_context_data(**kwargs)
        search_unit = self.search_unit

        context['collections_count'] = SearchUnitCollection.objects.filter(
            search_unit_id=search_unit.id).count()
        context['documents_count'] = SearchUnitDocument.objects.filter(
            collection__search_unit_id=search_unit.id).count()
        context['authors_count'] = Author.objects.filter(
            searchunitdocument__collection__search_unit_id=search_unit.id).distinct().count()

        return context


class SearchUnitDocumentDetailMixin(object):
    context_object_name = 'document'

    def get_object(self, queryset=None):
        queryset = queryset or self.model.objects.all()
        queryset = queryset.select_related('collection', 'collection__search_unit', 'publisher') \
            .prefetch_related('authors', 'attachments')
        return get_object_or_404(queryset, localidentifier=self.kwargs['localid'])
