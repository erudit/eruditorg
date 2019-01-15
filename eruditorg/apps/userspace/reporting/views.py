import csv

from django.urls import reverse
from django.http import HttpResponseRedirect
from django.http import StreamingHttpResponse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView

from core.reporting.client import client
from core.reporting.search import ReportingSearch
from core.reporting.search import search
from core.reporting.utils import Echo
from core.solrq.query import Q

from .forms import ReportingFilterForm


class ReportingFormView(FormView):
    """
    A generic view that defines the use of a form to filter articles in order
    to get a article counts from Solr.
    """
    form_class = ReportingFilterForm
    http_method_names = ['get', ]

    def get_form_kwargs(self):
        kwargs = {
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
            'data': self.request.GET,
        }
        return kwargs

    def get_solr_search(self):
        return search

    def get_query_from_cleaned_data(self, cleaned_data):
        """
        Returns the Query instance by using the form' cleaned
        data as filters.
        """
        # Prepares the Reporting query
        rq = self.get_solr_search()
        for k, v in cleaned_data.items():
            if not v:
                continue

            if isinstance(v, list):
                q = Q(**{k: v[0]})
                for iv in v[1:]:
                    q |= Q(**{k: iv})
                rq = rq.filter(q)
            else:
                rq = rq.filter(**{k: v})

        return rq

    def get_results_from_cleaned_data(self, cleaned_data):
        """
        Returns the pysolr Results instance by using the form' cleaned
        data as filters.
        """
        rq = self.get_query_from_cleaned_data(cleaned_data)
        results = rq.results
        return results


class ReportingHomeView(ReportingFormView):
    """
    Just a proof of concept view that allows to filter and to perform
    aggregations on the Érudit Solr index.
    """
    template_name = 'userspace/reporting/home.html'

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        results = self.get_results_from_cleaned_data(form.cleaned_data)

        # Prepares articles counts per year
        year_facet = results.facets['facet_fields']['AnneePublication']
        year_agg = list(zip(*[iter(year_facet)] * 2))

        # Prepares articles counts per journal
        journal_facet = results.facets['facet_fields']['RevueID']
        journal_agg = list(zip(*[iter(journal_facet)] * 2))

        # Prepares articles counts per issue
        issue_facet = results.facets['facet_fields']['NumeroID']
        issue_agg = list(zip(*[iter(issue_facet)] * 2))

        # Prepares articles counts per author
        author_facet = results.facets['facet_fields']['Auteur_tri']
        author_agg = list(zip(*[iter(author_facet)] * 2))

        # Prepares articles counts per type
        type_facet = results.facets['facet_fields']['Corpus_fac']
        type_agg = list(zip(*[iter(type_facet)] * 2))

        return self.render_to_response(
            self.get_context_data(
                form=form, results=results, year_agg=year_agg, journal_agg=journal_agg,
                issue_agg=issue_agg, author_agg=author_agg, type_agg=type_agg))

    def get_context_data(self, **kwargs):
        context = super(ReportingHomeView, self).get_context_data(**kwargs)

        # Includes the total number of articles in the context
        context['articles_count'] = search.results.hits

        return context


class ReportingCsvView(ReportingFormView):
    def get(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return HttpResponseRedirect(reverse('userspace:reporting:home'))

    def get_solr_search(self):
        search = ReportingSearch(client)
        search.extra_params = {
            'rows': 1000000,
            'group': 'true',
            'group.field': 'NumeroID',
            'fl': 'RevueID,AnneePublication',
            'sort': 'RevueID asc, AnneePublication asc',
        }
        return search

    def get_query_from_cleaned_data(self, cleaned_data):
        rq = super(ReportingCsvView, self).get_query_from_cleaned_data(cleaned_data)
        # We only want to retrieve 'Article' / 'Culturel' docs
        rq.filter(Q(type='Article') | Q(type='Culturel'))
        return rq

    def get_csv_rows(self, results):
        """ Returns the rows to insert into the final CSV. """
        raise NotImplementedError

    def form_valid(self, form):
        results = self.get_results_from_cleaned_data(form.cleaned_data)

        # Prepares the CSV
        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer)

        # Prepares the rows of the CSV
        rows = self.get_csv_rows(results)

        # Prepares the response ; we use a StreamingHttpResponse because we
        # can generate very large responses.
        response = StreamingHttpResponse(
            (writer.writerow(row) for row in rows), content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename"'

        return response


class ReportingIssueCsvView(ReportingCsvView):
    def get_solr_search(self):
        search = ReportingSearch(client)
        search.extra_params = {
            'rows': 1000000,
            'group': 'true',
            'group.field': 'NumeroID',
            'fl': 'RevueID,AnneePublication',
            'sort': 'RevueID asc, AnneePublication asc',
        }
        return search

    def get_csv_rows(self, results):
        # Prepares the rows of the CSV
        rows = [[_("Revue"), _("Numéro"), _("Année"), _("Nombre d'articles"), ]]
        for group in results.grouped['NumeroID']['groups']:
            rows.append([
                group['doclist']['docs'][0]['RevueID'],
                group['groupValue'],
                group['doclist']['docs'][0]['AnneePublication'],
                group['doclist']['numFound'],
            ])
        return rows


class ReportingJournalCsvView(ReportingCsvView):
    def get_solr_search(self):
        search = ReportingSearch(client)
        search.extra_params = {
            'rows': 1000000,
            'group': 'true',
            'group.field': 'RevueID',
            'fl': 'RevueID',
            'sort': 'RevueID asc',
        }
        return search

    def get_csv_rows(self, results):
        # Prepares the rows of the CSV
        rows = [[_("Revue"), _("Nombre d'articles"), ]]
        for group in results.grouped['RevueID']['groups']:
            rows.append([
                group['groupValue'],
                group['doclist']['numFound'],
            ])
        return rows
