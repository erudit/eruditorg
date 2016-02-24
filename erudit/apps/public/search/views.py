from math import ceil
from django.views.generic import FormView

from erudit.models import EruditDocument
from . import solr, forms

DOCUMENT_TYPES = {
    "journal": [
        "article",
        "culturel",
    ],
    "book": [],
    "thesis": [],
    "document": [],
}


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

    def get_solr_data(self, form):
        """Query solr"""
        self.search_term = form.cleaned_data.get("search_term", None)
        self.sort = form.cleaned_data.get("sort", None)
        self.sort_order = form.cleaned_data.get("sort_order", None)
        self.page = form.cleaned_data.get("page", 1)
        self.results_per_query = self.paginate_by
        self.start_at = ((self.page - 1) * self.results_per_query)

        if not self.search_term:
            return None

        else:
            try:
                solr_conn = solr.Solr()
                return solr_conn.simple_search(
                    search_term=self.search_term,
                    sort=self.sort,
                    sort_order=self.sort_order,
                    start_at=self.start_at,
                    results_per_query=self.results_per_query,
                )

            except:
                return None

    def get_queryset(self, solr_data):
        """Query Django models using Solr data"""

        doc_ids = []
        for doc in solr_data["response"]["docs"]:
            doc_id = doc.get("ID", None)

            if doc_id:
                doc_ids.append(doc_id)

        return self.model.objects.all().filter(localidentifier__in=doc_ids)

    def get(self, request, *args, **kwargs):
        """We want this form to handle GET method"""
        return self.post(request, *args, **kwargs)

    def get_form_kwargs(self):
        """We want this form to handle GET method"""
        kwargs = super(Search, self).get_form_kwargs()

        # If no search term, then not a search yet
        if self.request.GET.get("search_term", None):
            kwargs.update({'data': self.request.GET})

        return kwargs

    def get_initial(self):
        initial = super(Search, self).get_initial()

        initial["search_term"] = self.request.GET.get("search_term", None)
        initial["sort"] = self.request.GET.get("sort", None)
        initial["sort_order"] = self.request.GET.get("sort_order", None)
        initial["page"] = self.request.GET.get("page", 1)

        return initial

    def form_valid(self, form):
        solr_data = self.get_solr_data(form=form)

        try:
            self.results_count = solr_data["response"]["numFound"]
        except:
            self.results_count = 0

        try:
            self.page_count = ceil(self.results_count / self.results_per_query)
        except:
            self.page_count = 1

        self.object_list = self.get_queryset(solr_data=solr_data)

        # return super(Search, self).form_valid(form)
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super(Search, self).get_context_data(**kwargs)

        context[self.context_object_name] = self.object_list
        context["results_count"] = self.results_count
        context["page_count"] = self.page_count
        context["current_page"] = self.page

        return context
