# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django.views.generic import DetailView
from django.views.generic import ListView

from erudit.models import Author
from erudit.models import SearchUnit
from erudit.models import SearchUnitCollection
from erudit.models import SearchUnitDocument

from .viewmixins import SearchUnitStatsMixin


class SearchUnitListView(ListView):
    context_object_name = 'search_units'
    model = SearchUnit
    template_name = 'public/grey_literature/search_unit_list.html'

    def get_context_data(self, **kwargs):
        context = super(SearchUnitListView, self).get_context_data(**kwargs)
        context['global_search_units_count'] = SearchUnit.objects.all().count()
        context['global_documents_count'] = SearchUnitDocument.objects.all().count()
        context['global_authors_count'] = Author.objects.filter(
            searchunitdocument__isnull=False).distinct().count()
        return context


class SearchUnitDetailView(SearchUnitStatsMixin, DetailView):
    context_object_name = 'search_unit'
    model = SearchUnit
    template_name = 'public/grey_literature/search_unit_detail.html'

    def get_context_data(self, **kwargs):
        context = super(SearchUnitDetailView, self).get_context_data(**kwargs)
        context['new_documents'] = SearchUnitDocument.objects.filter(
            collection__search_unit_id=self.object.id).order_by('-publication_year')[:3]
        context['collections'] = SearchUnitCollection.objects.filter(search_unit_id=self.object.id)
        return context

    def get_object(self, queryset=None):
        queryset = queryset or self.model.objects.all()
        queryset = queryset.select_related('collection')
        return get_object_or_404(queryset, code=self.kwargs['code'])

    def get_search_unit(self):
        return self.object


class SearchUnitCollectionDetailView(SearchUnitStatsMixin, ListView):
    context_object_name = 'documents'
    paginate_by = 20
    template_name = 'public/grey_literature/collection_detail.html'

    @cached_property
    def collection(self):
        return self.get_collection()

    def get_collection(self):
        queryset = SearchUnitCollection.objects.select_related('search_unit').all()
        return get_object_or_404(queryset, localidentifier=self.kwargs['localid'])

    def get_context_data(self, **kwargs):
        context = super(SearchUnitCollectionDetailView, self).get_context_data(**kwargs)
        context['collection'] = self.collection
        context['search_unit'] = self.search_unit
        return context

    def get_queryset(self):
        return SearchUnitDocument.objects.select_related('collection').prefetch_related('authors') \
            .filter(collection=self.collection).order_by('title')

    def get_search_unit(self):
        return self.collection.search_unit
