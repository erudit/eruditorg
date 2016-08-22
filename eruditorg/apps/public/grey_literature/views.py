# -*- coding: utf-8 -*-

from django.views.generic import ListView

from erudit.models import Author
from erudit.models import SearchUnit
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
