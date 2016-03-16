import urllib
from math import ceil
from django.views.generic import FormView
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator

# from base.viewmixins import SolrServiceRequiredMixin
from erudit.models import EruditDocument
from . import solr, forms


# class Search(SolrServiceRequiredMixin, FormView):
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
    form_class = forms.SearchForm

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
        basic_search_term = data.get("basic_search_term", None)
        basic_search_field = data.get("basic_search_field", None)

        if basic_search_term:
            self.search_elements.append({
                "search_operator": basic_search_operator,
                "search_term": basic_search_term,
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
        # If not searching for anything, then don't handle search
        if "basic_search_term" not in request.GET:
            return self.render_to_response(self.get_context_data())

        else:
            return self.post(request=request, *args, **kwargs)
            # form = self.get_form()
            # if form.is_valid():
            #     return self.form_valid(form)
            # else:
            #     return self.form_invalid(form)

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
                self.page_count = ceil(self.results_count / self.results_per_query)
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
