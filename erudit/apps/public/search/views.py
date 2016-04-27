# -*- coding: utf-8 -*-

import json

from django.views.generic import View
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import FormMixin
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.utils.encoding import smart_text
from django.utils.translation import ugettext_lazy as _
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from erudit.models import EruditDocument
from erudit.serializers import EruditDocumentSerializer

from . import filters
from .forms import ADVANCED_SEARCH_FIELDS
from .forms import ResultsFilterForm
from .forms import ResultsOptionsForm
from .forms import SearchForm
from .pagination import EruditDocumentPagination


class EruditDocumentListAPIView(ListAPIView):
    pagination_class = EruditDocumentPagination
    queryset = EruditDocument.objects.all()
    search_engine_filter_backend = filters.EruditDocumentSolrFilter
    serializer_class = EruditDocumentSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # Applies the search engine filter backend in order to get a list of filtered
        # EruditDocument localidentifiers and a dictionnary contening the result of aggregations
        # that should be embedded in the final response object.
        localidentifiers, aggregations_dict = self.search_engine_filter_backend() \
            .filter(self.request, queryset, self)

        # Paginates the results
        page = self.paginate(localidentifiers, queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(queryset, many=True)
            response = Response(serializer.data)

        # Add aggregation data to the returned content
        response.data.update({'aggregations': aggregations_dict})

        return response

    def paginate(self, localidentifiers, queryset):
        return self.paginator.paginate(localidentifiers, queryset, self.request, view=self)


class SearchResultsView(TemplateResponseMixin, FormMixin, View):
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

    def get_search_elements(self):
        """ Returns the search query elements in a readable way.

        This should be used to express a query using the following format:

            (Titre, résumé, mots-clés : pedagogi*) ET (Titre, résumé, mots-clés : drama*) [...]

        """
        params = self.request.GET.copy()
        fields_correspondence = dict(ADVANCED_SEARCH_FIELDS)
        operator_correspondance = {
            'AND': _('ET'),
            'OR': _('OU'),
            'NOT': _('NON'),
        }

        search_elements = []

        def elements(t, f, o):
            f = fields_correspondence.get(f, f)
            o_, o = o, operator_correspondance.get(o, o)
            return {
                'term': t,
                'field': f,
                'operator': o_,
                'str': ('({field} : {term})'.format(field=f, term=t) if o is None
                        else '{op} ({field} : {term})'.format(op=o, field=f, term=t)),
            }

        q1_term = params.get('basic_search_term', '*')
        q1_field = params.get('basic_search_field', 'all')
        q1_operator = params.get('basic_search_operator', None)
        q1_operator = 'NOT' if q1_operator is not None else None
        search_elements.append(elements(q1_term, q1_field, q1_operator))

        return search_elements

    def get_context_data(self, **kwargs):
        context = super(SearchResultsView, self).get_context_data(**kwargs)
        results = context.get('results')

        context['main_qterm'] = self.request.GET.get('basic_search_term', '')
        context['start_at'] = (results['pagination']['current_page'] - 1) \
            * results['pagination']['page_size']
        context['search_elements'] = self.get_search_elements()

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
        raise NotImplementedError

    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(SearchResultsView, self).dispatch(*args, **kwargs)
