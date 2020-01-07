import logging

import copy
import urllib.parse as urlparse

from django.urls import reverse
from django.http import HttpResponseRedirect, QueryDict
from django.views.generic import View
from django.views.generic.base import ContextMixin
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import FormMixin
from django.utils.translation import gettext

from erudit.solr.models import get_model_instance
from base.http import JsonAckResponse
from base.http import JsonErrorResponse

from . import filters, legacy
from .forms import ResultsFilterForm
from .forms import ResultsOptionsForm
from .forms import SearchForm
from .pagination import PaginationOutOfBoundsException
from .saved_searches import SavedSearchList
from .utils import get_search_elements, GET_as_dict

logger = logging.getLogger(__name__)


class AdvancedSearchView(TemplateResponseMixin, FormMixin, View):
    """ Displays the search form in order to perform advanced searches for Érudit documents. """

    form_class = SearchForm
    http_method_names = [
        "get",
    ]
    template_name = "public/search/advanced_search.html"

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
            _saved_searches = reversed(sorted(saved_searches, key=lambda s: s["timestamp"]))
            sorted_saved_searches = []
            for search in _saved_searches:
                new_search = search.copy()
                qsdict = QueryDict(new_search["querystring"])
                new_search["elements"] = get_search_elements(qsdict)
                sorted_saved_searches.append(new_search)

            context["saved_searches"] = sorted_saved_searches

        return context

    def get_form_kwargs(self):
        kwargs = {"initial": self.get_initial(), "prefix": self.get_prefix()}
        if self.request.GET:
            MULTI = {
                "article_types",
                "publication_types",
                "funds",
                "disciplines",
                "languages",
                "journals",
            }
            kwargs["initial"].update(GET_as_dict(self.request.GET, MULTI))
        return kwargs


class SearchResultsView(TemplateResponseMixin, ContextMixin, View):
    """ Display the results associated with a search for Érudit documents. """

    filter_form_class = ResultsFilterForm
    http_method_names = [
        "get",
    ]
    options_form_class = ResultsOptionsForm
    search_form_class = SearchForm
    template_name = "public/search/results.html"

    def __init__(self):
        super().__init__()
        self._search_form = None

    def get(self, request, *args, **kwargs):
        # This view works only for GET requests
        self.request = copy.copy(self.request)
        search_form = self.get_search_form()
        options_form = self.get_options_form()
        search_form_valid, options_form_valid = search_form.is_valid(), options_form.is_valid()
        if search_form_valid and options_form_valid:
            return self.forms_valid(search_form, options_form)
        else:
            return self.forms_invalid(search_form, options_form)

    def get_search_form(self):
        """ Returns an instance of the search form to be used in this view. """
        if self._search_form is None:
            self._search_form = self.search_form_class(**self.get_search_form_kwargs())
        return self._search_form

    def get_search_form_kwargs(self):
        """ Returns the keyword arguments for instantiating the search form. """
        form_kwargs = {}

        if self.request.method == "GET":
            form_kwargs.update(
                {
                    "data": self.request.GET,
                }
            )
        return form_kwargs

    def get_filter_form(self, **kwargs):
        """ Returns an instance of the filter form to be used in this view. """
        return self.filter_form_class(**self.get_filter_form_kwargs(**kwargs))

    def get_filter_form_kwargs(self, **kwargs):
        """ Returns the keyword arguments for instantiating the filter form. """
        form_kwargs = {}
        form_kwargs.update(kwargs)

        if self.request.method == "GET":
            form_kwargs.update(
                {
                    "data": self.request.GET,
                }
            )
        return form_kwargs

    def get_options_form(self):
        """ Returns an instance of the options form to be used in this view. """
        return self.options_form_class(**self.get_options_form_kwargs())

    def get_options_form_kwargs(self):
        """ Returns the keyword arguments for instantiating the options form. """
        form_kwargs = {}

        self.request.GET = legacy.add_correspondences_to_search_query(
            self.request, "filter_article_types", self.filter_form_class.article_type_correspondence
        )

        self.request.GET = legacy.add_correspondences_to_search_query(
            self.request, "filter_languages", self.filter_form_class.language_code_correspondence
        )

        if self.request.method == "GET":
            form_kwargs.update(
                {
                    "data": self.request.GET,
                }
            )
        return form_kwargs

    def get_context_data(self, **kwargs):
        context = super(SearchResultsView, self).get_context_data(**kwargs)
        results = context.get("results", None)

        if results:
            context["main_qterm"] = self.request.GET.get("basic_search_term", "")
            context["start_at"] = (results["pagination"]["current_page"] - 1) * results[
                "pagination"
            ]["page_size"]
            context["search_elements"] = get_search_elements(
                self.request.GET, form=self.get_search_form()
            )

        return context

    def forms_valid(self, search_form, options_form):
        # Applies the search engine filter backend in order to get a list of filtered
        # EruditDocument localidentifiers, a dictionnary contening the result of aggregations
        # that should be embedded in the final response object and a number of hits.

        try:
            pagination_info, documents, aggregations_dict = filters.SolrFilter().filter(
                self.request
            )
        except PaginationOutOfBoundsException:
            return HttpResponseRedirect(reverse("public:search:advanced_search"))

        solr_objects = [get_model_instance(document) for document in documents]
        results = {
            "pagination": pagination_info,
            "results": solr_objects,
            "aggregations": aggregations_dict,
        }

        # Initializes the filters form here in order to display it using choices generated from the
        # aggregations embedded in the results.
        filter_form = self.get_filter_form(api_results=results)

        return self.render_to_response(
            self.get_context_data(
                search_form=search_form,
                filter_form=filter_form,
                options_form=options_form,
                results=results,
                documents=results.get("results"),
            )
        )

    def forms_invalid(self, search_form, options_form):
        GET = self.request.GET
        if "basic_search_term" not in GET:
            # This is simply a case of typing the /recherche/ url directly. We don't want to log
            # those.
            pass
        elif "basic_search_term" in GET and not GET.get("basic_search_term"):
            # This is simply a case of clicking on homepage's search magnifier without a search
            # param. We don't want to log those, we just want to silently redirect.
            pass
        else:
            # We have some unhandled form validation here that we'd like to know about.
            logger.error(
                "search.form.invalid",
                extra={
                    "stack": True,
                    "search_form_errors": search_form.errors.as_json(),
                    "options_form_errors": options_form.errors.as_json(),
                },
            )
        return HttpResponseRedirect(
            "{}?{}".format(reverse("public:search:advanced_search"), self.request.GET.urlencode())
        )


class SavedSearchAddView(View):
    """ Add a search's querystring to the list of saved searches associated to the current user. """

    http_method_names = [
        "post",
    ]

    def post(self, request):
        try:
            querystring = request.POST.get("querystring", None)
            results_count = request.POST.get("results_count", None)
            assert querystring is not None
            assert results_count is not None
            parsed_qstring = urlparse.parse_qsl(querystring)
            assert parsed_qstring
            results_count = int(results_count)
        except (AssertionError, ValueError):
            return JsonErrorResponse(gettext("Querystring incorrecte"))

        # Inserts the search into the saved searches set
        searches = SavedSearchList(request)
        searches.add(querystring, results_count)
        searches.save()

        return JsonAckResponse()


class SavedSearchRemoveView(View):
    """ Remove a saved search from the list of saved searches associated to the current user. """

    http_method_names = [
        "post",
    ]

    def post(self, request, uuid):
        searches = SavedSearchList(request)
        try:
            searches.remove(uuid)
        except ValueError:
            return JsonErrorResponse(gettext("Cette recherche n'est pas sauvegardée"))

        searches.save()
        return JsonAckResponse()
