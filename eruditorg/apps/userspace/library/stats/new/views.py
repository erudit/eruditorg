# -*- coding: utf-8 -*-

import csv
import datetime as dt

from django.http import HttpResponse
from django.views.generic import View

from erudit.models import Journal

from django.contrib.auth.mixins import LoginRequiredMixin
from core.counter.counter import JournalReport1
from core.counter.counter import JournalReport1GOA
from core.counter.csv import get_csv_journal_counter_report_rows
from core.counter.xml import get_xml_journal_counter_report

from apps.userspace.library.viewmixins import OrganisationScopePermissionRequiredMixin


class CounterJournalReportView(LoginRequiredMixin, OrganisationScopePermissionRequiredMixin, View):
    http_method_names = ['get', ]
    permission_required = 'subscription.access_library_stats'
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
        nowd = dt.datetime.now().date()
        subscription = self.current_organisation.journalaccesssubscription_set.filter(
            journalaccesssubscriptionperiod__start__lte=nowd,
            journalaccesssubscriptionperiod__end__gte=nowd,
        ).first()
        return subscription.get_journals() if subscription else Journal.objects.none()

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
    def render_report(self, report):
        """ Renders the Counter report as a CSV file. """
        # Prepares the response object
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="counter-{0}-{1}.csv"'.format(
            report.start.isoformat(), report.end.isoformat())

        # Writes the CSV rows
        writer = csv.writer(response)
        writer.writerows(
            get_csv_journal_counter_report_rows(
                report, organisation_name=self.current_organisation.name))

        return response


class CounterJournalReport1CsvView(CounterJournalReportCsvView):
    report_class = JournalReport1


class CounterJournalReport1GOACsvView(CounterJournalReportCsvView):
    report_class = JournalReport1GOA


class CounterJournalReportXmlView(CounterJournalReportView):
    def render_report(self, report):
        """ Renders the Counter report as a XML file. """
        return HttpResponse(
            get_xml_journal_counter_report(report, self.current_organisation.name),
            content_type='text/xml')


class CounterJournalReport1XmlView(CounterJournalReportXmlView):
    report_class = JournalReport1


class CounterJournalReport1GOAXmlView(CounterJournalReportXmlView):
    report_class = JournalReport1GOA
