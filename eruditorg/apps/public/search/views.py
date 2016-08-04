# -*- coding: utf-8 -*-

import json
import urllib.parse as urlparse

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http import QueryDict
from django.views.generic import View
from django.views.generic.base import ContextMixin
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import FormMixin
from django.utils.encoding import smart_text
from django.utils.translation import ugettext
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from erudit.models import EruditDocument

from base.http import JsonAckResponse
from base.http import JsonErrorResponse

from . import filters
from .forms import ResultsFilterForm
from .forms import ResultsOptionsForm
from .forms import SearchForm
from .pagination import EruditDocumentPagination
from .saved_searches import SavedSearchList
from .serializers import EruditDocumentSerializer
from .utils import get_search_elements


class EruditDocumentListAPIView(ListAPIView):
    authentication_classes = []
    pagination_class = EruditDocumentPagination
    queryset = EruditDocument.objects.all()
    search_engine_filter_backend = filters.EruditDocumentSolrFilter
    serializer_class = EruditDocumentSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # Applies the search engine filter backend in order to get a list of filtered
        # EruditDocument localidentifiers, a dictionnary contening the result of aggregations
        # that should be embedded in the final response object and a number of hits.
        docs_count, localidentifiers, aggregations_dict = self.search_engine_filter_backend() \
            .filter(self.request, queryset, self)

        # Paginates the results
        page = self.paginate(docs_count, localidentifiers, queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
        else:  # pragma: no cover
            # This can happen if we pass page_size = 0
            serializer = self.get_serializer(queryset, many=True)
            response = Response(serializer.data)

        # Add aggregation data to the returned content
        response.data.update({'aggregations': aggregations_dict})

        return response

    def paginate(self, docs_count, localidentifiers, queryset):
        return self.paginator.paginate(
            docs_count, localidentifiers, queryset, self.request, view=self)


class AdvancedSearchView(TemplateResponseMixin, FormMixin, View):
    """ Displays the search form in order to perform advanced searches for Érudit documents. """
    form_class = SearchForm
    http_method_names = ['get', ]
    template_name = 'public/search/advanced_search.html'

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        if request.GET:
            form.is_valid()
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super(AdvancedSearchView, self).get_context_data(**kwargs)

        # Prepares the saved searches, generates the search elements for each querystring and
        # inserts them into the context.
        saved_searches = SavedSearchList(self.request)
        if saved_searches:
            _saved_searches = reversed(sorted(saved_searches, key=lambda s: s['timestamp']))
            sorted_saved_searches = []
            for search in _saved_searches:
                new_search = search.copy()
                qsdict = QueryDict(new_search['querystring'])
                new_search['elements'] = get_search_elements(qsdict)
                sorted_saved_searches.append(new_search)

            context['saved_searches'] = sorted_saved_searches

        return context

    def get_form_kwargs(self):
        kwargs = {'initial': self.get_initial(), 'prefix': self.get_prefix()}
        if self.request.GET:
            kwargs.update({'data': self.request.GET})
        return kwargs


class SearchResultsView(TemplateResponseMixin, ContextMixin, View):
    """ Display the results associated with a search for Érudit documents. """
    filter_form_class = ResultsFilterForm
    http_method_names = ['get', ]
    options_form_class = ResultsOptionsForm
    search_form_class = SearchForm
    template_name = 'public/search/results.html'

    def get(self, request, *args, **kwargs):
        # This view works only for GET requests
        search_form = self.get_search_form()
        options_form = self.get_options_form()
        search_form_valid, options_form_valid = search_form.is_valid(), options_form.is_valid()
        if search_form_valid and options_form_valid:
            return self.forms_valid(search_form, options_form)
        else:
            return self.forms_invalid(search_form, options_form)

    def get_search_form(self):
        """ Returns an instance of the search form to be used in this view. """
        return self.search_form_class(**self.get_search_form_kwargs())

    def get_search_form_kwargs(self):
        """ Returns the keyword arguments for instantiating the search form. """
        form_kwargs = {}

        if self.request.method == 'GET':
            form_kwargs.update({'data': self.request.GET, })
        return form_kwargs

    def get_filter_form(self, **kwargs):
        """ Returns an instance of the filter form to be used in this view. """
        return self.filter_form_class(**self.get_filter_form_kwargs(**kwargs))

    def get_filter_form_kwargs(self, **kwargs):
        """ Returns the keyword arguments for instantiating the filter form. """
        form_kwargs = {}
        form_kwargs.update(kwargs)

        if self.request.method == 'GET':
            form_kwargs.update({'data': self.request.GET, })
        return form_kwargs

    def get_options_form(self):
        """ Returns an instance of the options form to be used in this view. """
        return self.options_form_class(**self.get_options_form_kwargs())

    def get_options_form_kwargs(self):
        """ Returns the keyword arguments for instantiating the options form. """
        form_kwargs = {}

        if self.request.method == 'GET':
            form_kwargs.update({'data': self.request.GET, })
        return form_kwargs

    def get_context_data(self, **kwargs):
        context = super(SearchResultsView, self).get_context_data(**kwargs)
        results = context.get('results', None)

        if results:
            context['main_qterm'] = self.request.GET.get('basic_search_term', '')
            context['start_at'] = (results['pagination']['current_page'] - 1) \
                * results['pagination']['page_size']
            context['search_elements'] = get_search_elements(self.request.GET)

        return context

    def forms_valid(self, search_form, options_form):
        # The form is valid so we have to retrieve the list of results by using the API view
        # returning EruditDocument documents.
        list_view = EruditDocumentListAPIView.as_view()
        request = self.request
        request.GET = request.GET.copy()  # A QueryDict is immutable
        request.GET.setdefault('format', 'json')
        results_data = list_view(request).render().content
        results = json.loads(smart_text(results_data))

        # Initializes the filters form here in order to display it using choices generated from the
        # aggregations embedded in the results.
        filter_form = self.get_filter_form(api_results=results)

        return self.render_to_response(self.get_context_data(
            search_form=search_form, filter_form=filter_form, options_form=options_form,
            results=results, documents=results.get('results')))

    def forms_invalid(self, search_form, options_form):
        return HttpResponseRedirect(
            '{}?{}'.format(reverse('public:search:advanced_search'), self.request.GET.urlencode()))


class SavedSearchAddView(View):
    """ Add a search's querystring to the list of saved searches associated to the current user. """
    http_method_names = ['post', ]

    def post(self, request):
        try:
            querystring = request.POST.get('querystring', None)
            results_count = request.POST.get('results_count', None)
            assert querystring is not None
            assert results_count is not None
            parsed_qstring = urlparse.parse_qsl(querystring)
            assert parsed_qstring
            results_count = int(results_count)
        except (AssertionError, ValueError):
            return JsonErrorResponse(ugettext("Querystring incorrecte"))

        # Inserts the search into the saved searches set
        searches = SavedSearchList(request)
        searches.add(querystring, results_count)
        searches.save()

        return JsonAckResponse()


class SavedSearchRemoveView(View):
    """ Remove a saved search from the list of saved searches associated to the current user. """
    http_method_names = ['post', ]

    def post(self, request, uuid):
        searches = SavedSearchList(request)
        try:
            searches.remove(uuid)
        except ValueError:
            return JsonErrorResponse(ugettext("Cette recherche n'est pas sauvegardée"))

        searches.save()
        return JsonAckResponse()
