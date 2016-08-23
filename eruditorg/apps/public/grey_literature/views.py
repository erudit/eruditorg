# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from django.views.generic import ListView

from erudit.models import Author
from erudit.models import SearchUnit
from erudit.models import SearchUnitCollection
from erudit.models import SearchUnitDocument


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


class SearchUnitDetailView(DetailView):
    context_object_name = 'search_unit'
    model = SearchUnit
    template_name = 'public/grey_literature/search_unit_detail.html'

    def get_context_data(self, **kwargs):
        context = super(SearchUnitDetailView, self).get_context_data(**kwargs)
        documents_qs = SearchUnitDocument.objects.filter(collection__search_unit_id=self.object.id)
        collections_qs = SearchUnitCollection.objects.filter(search_unit_id=self.object.id)
        context['new_documents'] = documents_qs.order_by('-publication_year')[:3]
        context['collections_count'] = collections_qs.count()
        context['documents_count'] = documents_qs.count()
        context['authors_count'] = Author.objects.filter(
            searchunitdocument__collection__search_unit_id=self.object.id).distinct().count()
        context['collections'] = collections_qs
        return context

    def get_object(self, queryset=None):
        queryset = queryset or SearchUnit.objects.all()
        queryset = queryset.select_related('collection')
        return get_object_or_404(queryset, code=self.kwargs['code'])
