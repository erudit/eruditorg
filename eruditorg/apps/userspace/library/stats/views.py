# -*- coding: utf-8 -*-

import csv
import datetime as dt

from django.http import HttpResponse
from django.views.generic import View

from base.viewmixins import LoginRequiredMixin

from ..viewmixins import OrganisationScopePermissionRequiredMixin
from .counter import JournalReport1
from .counter import JournalReport1GOA


class CounterJournalReportView(LoginRequiredMixin, OrganisationScopePermissionRequiredMixin, View):
    http_method_names = ['get', ]
    permission_required = 'subscription.manage_organisation_subscription_ips'
    report_class = None

    def get(self, request, organisation_pk):
        # Get the report parameters
        dstart, dend = self.get_report_period(request)
        # Get the report
        report = self.get_report(dstart, dend)
        return self.render_report(report)

    def get_report(self, dstart, dend):
        """ Returns a CounterReport instance. """
        return self.report_class(dstart, dend, journal_queryset=self.get_report_journal_queryset())

    def get_report_journal_queryset(self):
        """ Returns a queryset of the Journal instances that should be exposed in the report. """
        return None

    def get_report_period(self, request):
        """ Returns a tuple (start date, end date) containing the period of the report. """
        params = request.GET.copy()
        now_dt = dt.datetime.now()

        start = params.get('start', None)
        end = params.get('end', None)
        year = params.get('year', None)

        # First handles the case where a precise period has been specified
        try:
            dstart = dt.datetime.strptime(start, '%Y-%m-%d').date()
            dend = dt.datetime.strptime(end, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            dstart, dend = None, None
        else:
            return dstart, dend

        # Then handles the case where a year has been specified
        try:
            year = int(year)
            assert year <= now_dt.year
        except (ValueError, TypeError, AssertionError):
            dstart, dend = None, None
        else:
            return dt.date(year, 1, 1), dt.date(year, 12, 31)

        # We cannot determine the period to consider so we use the current year
        return dt.date(now_dt.year, 1, 1), dt.date(now_dt.year, 12, 31)

    def render_report(self, dstart, dend):
        """ Renders the Counter report. """
        raise NotImplementedError


class CounterJournalReportCsvView(CounterJournalReportView):
    def get_csv_rows(self, report):
        """ Returns the rows to write into the Counter CSV report. """
        rows = []

        # Add the header rows
        rows.append([report.title, report.subtitle])
        rows.append([self.current_organisation.name])
        rows.append([])
        rows.append(['Period covered by Report'])
        rows.append(['{start} to {end}'.format(
            start=report.start.isoformat(), end=report.end.isoformat())])
        rows.append(['Date run'])
        rows.append([dt.datetime.now().isoformat()])

        # Add the sub-header row
        rows.append([
            'Journal', 'Publisher', 'Platform', 'Journal DOI', 'Proprietary Identifier',
            'Print ISSN', 'Online ISSN', 'Reporting Period Total', 'Reporting Period HTML',
            'Reporting Period PDF',
        ] + [m['period_title'] for m in report.months])

        # Add the "total" row
        rows.append([
            'Total for all journals',
            '',  # Publisher
            '',  # Platform
            '',  # Journal DOI
            '',  # Proprietary Identifier
            '',  # Print ISSN
            '',  # Online ISSN
            report.total['reporting_period_total'],
            report.total['reporting_period_html'],
            report.total['reporting_period_pdf'],
        ] + report.total['months'])

        for jdata in report.journals:
            rows.append([
                jdata['journal'].name,
                jdata['journal'].publishers.first(),
                jdata['journal'].collection.name,
                '',  # Journal DOI
                '',  # Proprietary Identifier
                jdata['journal'].issn_print,
                jdata['journal'].issn_web,
                jdata['reporting_period_total'],
                jdata['reporting_period_html'],
                jdata['reporting_period_pdf'],
            ] + jdata['months'])

        return rows

    def render_report(self, report):
        """ Renders the Counter report as a CSV file. """
        # Prepares the response object
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="counter-{0}-{1}.csv"'.format(
            report.start.isoformat(), report.end.isoformat())

        # Writes the CSV rows
        writer = csv.writer(response)
        writer.writerows(self.get_csv_rows(report))

        return response


class CounterJournalReport1CsvView(CounterJournalReportCsvView):
    report_class = JournalReport1


class CounterJournalReport1GOACsvView(CounterJournalReportCsvView):
    report_class = JournalReport1GOA
