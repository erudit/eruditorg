# -*- coding: utf-8 -*-

import json
import math
import urllib

from django.views.generic import FormView
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
from . import solr
from .forms import ADVANCED_SEARCH_FIELDS
from .forms import FilterResultsForm
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
    filter_form_class = FilterResultsForm
    filter_form_prefix = 'filter'
    http_method_names = ['get', ]
    search_form_class = SearchForm
    search_form_prefix = None
    template_name = 'public/search/results.html'

    def get(self, request, *args, **kwargs):
        # This view works only for GET requests
        search_form = self.get_search_form()
        filter_form = self.get_filter_form()
        search_form_valid, filter_form_valid = search_form.is_valid(), filter_form.is_valid()
        if search_form_valid and filter_form_valid:
            return self.forms_valid(search_form, filter_form)
        else:
            return self.forms_invalid(search_form)

    def get_search_form(self, form_class=None):
        """ Returns an instance of the search form to be used in this view. """
        return self.search_form_class(**self.get_search_form_kwargs())

    def get_search_form_kwargs(self):
        """ Returns the keyword arguments for instantiating the search form. """
        kwargs = {'prefix': self.search_form_prefix}

        if self.request.method == 'GET':
            kwargs.update({'data': self.request.GET, })
        return kwargs

    def get_filter_form(self, form_class=None):
        """ Returns an instance of the filter form to be used in this view. """
        return self.filter_form_class(**self.get_filter_form_kwargs())

    def get_filter_form_kwargs(self):
        """ Returns the keyword arguments for instantiating the filter form. """
        kwargs = {'prefix': self.filter_form_prefix}

        if self.request.method == 'GET':
            kwargs.update({'data': self.request.GET, })
        return kwargs

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

    def forms_valid(self, search_form, filter_form):
        # The form is valid so we have to retrieve the list of results by using the API view
        # returning EruditDocument documents.
        list_view = EruditDocumentListAPIView.as_view()
        request = self.request
        request.GET = request.GET.copy()  # A QueryDict is immutable
        request.GET.setdefault('format', 'json')
        results_data = list_view(request).render().content
        results = json.loads(smart_text(results_data))

        # Initializes the filters form

        return self.render_to_response(self.get_context_data(
            search_form=search_form, results=results, documents=results.get('results')))

    def forms_invalid(self, search_form, filter_form):
        raise NotImplementedError

    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(SearchResultsView, self).dispatch(*args, **kwargs)


class Search(FormView):
    model = EruditDocument
    object_list = []
    results_count = None
    paginate_by = 25
    results_count = 0
    page_count = 1
    page = 1
    context_object_name = "documents"
    template_name = "public/search/search.html"
    form_class = SearchForm

    def __init__(self, *args, **kwargs):
        self.solr_conn = solr.Solr()
        self.limit_filter_fields = [
            "years",
            "article_types",
            "languages",
            "collections",
            "authors",
            "funds",
            "publication_types",
        ]   # Filter fields available
        self.filter_choices = {}
        self.selected_filters = {}
        self.search_elements = []
        self.search_extras = {}
        self.query_url = None

        return super(Search, self).__init__(*args, **kwargs)

    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(Search, self).dispatch(*args, **kwargs)

    def get_solr_data(self, form):
        """Query solr"""
        data = form.cleaned_data

        # Simple search
        basic_search_operator = data.get("basic_search_operator", None)
        basic_search_term = data.get("basic_search_term", '*')
        basic_search_field = data.get("basic_search_field", None)

        self.search_elements.append({
            "search_operator": "NOT" if basic_search_operator else basic_search_operator,
            "search_term": basic_search_term or '*',
            "search_field": basic_search_field,
        })

        # Advanced search
        for i in range(10):
            advanced_search_operator = data.get(
                "advanced_search_operator{counter}".format(counter=i + 1), None
            )
            advanced_search_term = data.get(
                "advanced_search_term{counter}".format(counter=i + 1), None
            )
            advanced_search_field = data.get(
                "advanced_search_field{counter}".format(counter=i + 1), None
            )

            if advanced_search_term:
                self.search_elements.append({
                    "search_operator": advanced_search_operator,
                    "search_term": advanced_search_term,
                    "search_field": advanced_search_field,
                })

        # Publication year
        if data.get("pub_year_start", None) or data.get("pub_year_end", None):
            self.search_extras["publication_date"] = {}
            self.search_extras["publication_date"]["pub_year_start"] = \
                data.get("pub_year_start", None)
            self.search_extras["publication_date"]["pub_year_end"] = \
                data.get("pub_year_end", None)

        # Document available since date
        self.search_extras["available_since"] = \
            data.get("available_since", None)

        # Document available since date
        self.search_extras["funds"] = \
            data.get("funds_limit", None)

        # Sorting / Pagination
        self.sort = data.get("sort", None)
        self.sort_order = data.get("sort_order", None)
        self.page = data.get("page", 1) if data.get("page", 1) else 1
        self.results_per_query = self.paginate_by
        self.start_at = ((self.page - 1) * self.results_per_query)

        # If nothing has been searched for, return nothing
        if not (self.search_elements):
            return None

        else:
            try:
                return self.solr_conn.search(
                    search_elements=self.search_elements,
                    search_extras=self.search_extras,
                    sort=self.sort,
                    sort_order=self.sort_order,
                    start_at=self.start_at,
                    results_per_query=self.results_per_query,
                    limit_filter_fields=self.limit_filter_fields,
                    selected_filters=self.selected_filters,
                )
            except:
                return None

    def get_queryset(self, doc_ids):
        """Query Django models using Solr data"""
        return self.model.objects.all().filter(localidentifier__in=doc_ids)

    def get(self, request, *args, **kwargs):
        """We want this form to handle GET method"""
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_form_kwargs(self):
        """We want this form to handle GET method"""
        kwargs = super(Search, self).get_form_kwargs()

        kwargs.update({'data': self.request.GET})

        return kwargs

    def get_initial(self):
        initial = super(Search, self).get_initial()

        # Get selected filter fields
        for field in self.limit_filter_fields:
            if self.request.GET.get(field, None):
                filter_value = self.request.GET.getlist(field, None)
                # Don't fill selected_filters with empty values
                if filter_value:
                    # Clean and quote filters
                    cleaned_value = [urllib.parse.unquote_plus(value) for value in filter_value]
                    self.selected_filters[field] = cleaned_value

        return initial

    def form_valid(self, form):
        self.query_url, solr_data = self.get_solr_data(form=form)

        if solr_data:
            # Number of results returned by Solr
            self.results_count = solr_data["results_count"]

            # Number of pages
            try:
                self.page_count = math.ceil(self.results_count / self.results_per_query)
            except:
                self.page_count = 1

            # Buld available filters
            self.filter_choices = solr_data["filter_choices"]

            # Get EruditDocument objects from returned IDs
            self.object_list = self.get_queryset(doc_ids=solr_data["doc_ids"])

        # return super(Search, self).form_valid(form)
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()

        context = super(Search, self).get_context_data(**kwargs)

        context[self.context_object_name] = self.object_list
        context["results_count"] = self.results_count
        context["page_count"] = self.page_count
        context["start_at"] = self.start_at
        context["current_page"] = self.page
        context["search_elements"] = self.search_elements
        context["filter_choices"] = self.filter_choices
        context["selected_filters"] = self.selected_filters
        context["query_url"] = self.query_url

        return context
