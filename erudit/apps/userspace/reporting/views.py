# -*- coding: utf-8 -*-

from django.views.generic import FormView

from core.reporting.query import ReportingQuery

from .forms import ReportingFilterForm


class ReportingHomeView(FormView):
    """
    Just a proof of concept view that allows to filter and to perform
    aggregations on the Érudit Solr index.
    """
    form_class = ReportingFilterForm
    http_method_names = ['get', ]
    template_name = 'userspace/reporting/home.html'

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_form_kwargs(self):
        kwargs = {
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
            'data': self.request.GET,
        }
        return kwargs

    def form_valid(self, form):
        # Prepares the Reporting query
        rq = ReportingQuery()
        rq = rq.filter(**{k: v for k, v in form.cleaned_data.items() if v})
        results = rq.results

        # Prepares articles counts per year
        year_facet = results.facets['facet_fields']['AnneePublication']
        year_agg = list(zip(*[iter(year_facet)]*2))

        # Prepares articles counts per issue
        issue_facet = results.facets['facet_fields']['NumeroID']
        issue_agg = list(zip(*[iter(issue_facet)]*2))

        # Prepares articles counts per author
        author_facet = results.facets['facet_fields']['Auteur_tri']
        author_agg = list(zip(*[iter(author_facet)]*2))

        return self.render_to_response(
            self.get_context_data(
                form=form, results=results, year_agg=year_agg, issue_agg=issue_agg,
                author_agg=author_agg))

    def get_context_data(self, **kwargs):
        context = super(ReportingHomeView, self).get_context_data(**kwargs)

        # Includes the total number of articles in the context
        context['articles_count'] = len(ReportingQuery().results)

        return context
