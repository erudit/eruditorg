# -*- coding: utf-8 -*-
import datetime as dt
import requests

from django.http import HttpResponse
from django.views.generic import View

from base.viewmixins import LoginRequiredMixin
from core.counter.counter import JournalReport1
from core.counter.counter import JournalReport1GOA
from core.counter.xml import get_xml_journal_counter_report

from apps.userspace.library.viewmixins import OrganisationScopePermissionRequiredMixin


class ExternalCounterReportView(LoginRequiredMixin, OrganisationScopePermissionRequiredMixin, View):
    http_method_names = ['get', ]
    permission_required = 'subscription.access_library_stats'
    report_base_url = "http://php.prod.erudit.org/counterphp/"

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

    def get(self, request, organisation_pk):
        # Get the report parameters
        dstart, dend = self.get_report_period(request)
        # Get the report
        report = self.get_report(dstart, dend)
        return report


class CounterJournalReportCsvView(ExternalCounterReportView):

    def get_report_arguments(self):
        return {}

    def get_report(self, dstart, dend):
        account_id = self.current_organisation.legacyorganisationprofile.account_id
        base_report_arguments = {'beginPeriod': dstart, 'endPeriod': dend, 'id': account_id}
        base_report_arguments.update(self.get_report_arguments())
        report = requests.get(self.report_base_url, params=base_report_arguments)
        filename = "{}-{}-{}".format(account_id, dstart, dend)
        response = HttpResponse(report, content_type="application/csv")
        response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(filename)
        return response


class CounterJournalReport1CsvView(CounterJournalReportCsvView):
    pass


class CounterJournalReport1GOACsvView(CounterJournalReportCsvView):

    def get_report_arguments(self):
        return {'isGoldOpenAccess': 'true'}


class CounterJournalReportXmlView(ExternalCounterReportView):
    def render_report(self, report):
        """ Renders the Counter report as a XML file. """
        return HttpResponse(
            get_xml_journal_counter_report(report, self.current_organisation.name),
            content_type='text/xml')


class CounterJournalReport1XmlView(CounterJournalReportXmlView):
    report_class = JournalReport1


class CounterJournalReport1GOAXmlView(CounterJournalReportXmlView):
    report_class = JournalReport1GOA
