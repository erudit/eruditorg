# -*- coding: utf-8 -*-
import datetime as dt
import requests

from django.http import HttpResponse
from django.views.generic import TemplateView
from .settings import ERUDIT_COUNTER_BACKEND_URL

from django.contrib.auth.mixins import LoginRequiredMixin
from base.viewmixins import MenuItemMixin

from apps.userspace.library.viewmixins import OrganisationScopePermissionRequiredMixin

from .forms import CounterJR1Form
from .forms import CounterJR1GOAForm


class StatsLandingView(
        LoginRequiredMixin, MenuItemMixin, OrganisationScopePermissionRequiredMixin, TemplateView):

    menu_library = 'stats'
    permission_required = 'library.has_access_to_dashboard'
    template_name = 'userspace/library/stats/legacy/landing.html'
    report_base_url = ERUDIT_COUNTER_BACKEND_URL
    counter_jr1_form = CounterJR1Form
    counter_jr1goa_form = CounterJR1GOAForm

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if context['requested_report'] == 'counter-jr1':
            form = context['counter_jr1_form']
        elif context['requested_report'] == 'counter-jr1-goa':
            form = context['counter_jr1goa_form']
        else:
            form = None
        if form and form.is_valid():
            # Get the report
            report = self.get_report(form.cleaned_data)
            return report
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(StatsLandingView, self).get_context_data(**kwargs)

        context['requested_report'] = self.get_requested_report()
        if context['requested_report'] == 'counter-jr1':
            context['counter_jr1_form'] = self.counter_jr1_form(
                organisation=self.current_organisation,
                data=self.request.GET
            )
            context['counter_jr1goa_form'] = self.counter_jr1goa_form(
                organisation=self.current_organisation
            )
        elif context['requested_report'] == 'counter-jr1-goa':
            context['counter_jr1_form'] = self.counter_jr1_form(
                organisation=self.current_organisation
            )
            context['counter_jr1goa_form'] = self.counter_jr1goa_form(
                organisation=self.current_organisation,
                data=self.request.GET
            )
        else:
            context['counter_jr1_form'] = self.counter_jr1_form(
                organisation=self.current_organisation
            )
            context['counter_jr1goa_form'] = self.counter_jr1goa_form(
                organisation=self.current_organisation
            )
        return context

    def get_requested_report(self):
        report_type = None
        if self.request.GET.get("{}-report_type".format(self.counter_jr1_form.prefix)):
            report_type = 'counter-jr1'
        elif self.request.GET.get("{}-report_type".format(self.counter_jr1goa_form.prefix)):
            report_type = 'counter-jr1-goa'
        return report_type

    def get_report(self, form_data):
        dstart, dend = self.get_report_period(form_data)
        # report_arguments = form_data
        report_arguments = {}
        report_arguments['format'] = form_data['format']
        report_arguments['id'] = self.current_organisation.legacyorganisationprofile.account_id
        report_arguments['beginPeriod'] = dstart.strftime("%Y-%m-%d")
        report_arguments['endPeriod'] = dend.strftime("%Y-%m-%d")
        if form_data.get('report_type') == 'counter-jr1-goa':
            report_arguments['isGoldOpenAccess'] = True

        format = report_arguments['format']
        report = requests.get(self._get_report_url(format), params=report_arguments)
        filename = "{id}-{beginPeriod}-{endPeriod}".format(**report_arguments)
        response = HttpResponse(
            report, content_type="application/{format}".format(**report_arguments)
        )
        response['Content-Disposition'] = 'attachment; filename="{filename}.{format}"'.format(
            filename=filename, format=format
        )
        return response

    def get_report_period(self, form_data):
        """ Returns a tuple (start date, end date) containing the period of the report. """
        now_dt = dt.datetime.now()
        year = form_data .get('year', None)
        month_start = form_data .get('month_start', None)
        month_end = form_data .get('month_end', None)
        year_start = form_data .get('year_start', None)
        year_end = form_data .get('year_end', None)

        # First handles the case where a precise period has been specified
        try:
            dstart_str = "{year}-{month}-01".format(year=year_start, month=month_start)
            dstart = dt.datetime.strptime(dstart_str, '%Y-%m-%d').date()
            dend_str = "{year}-{month}-01".format(year=year_end, month=month_end)
            dend = dt.datetime.strptime(dend_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            dstart, dend = None, None
        else:
            return dstart, dend

        # Then handles
        try:
            year = int(year)
            assert year <= now_dt.year
        except (ValueError, TypeError, AssertionError):
            dstart, dend = None, None
        else:
            return dt.date(year, 1, 1), dt.date(year, 12, 31)

        # We cannot determine the period to consider so we use the current year
        return dt.date(now_dt.year, 1, 1), dt.date(now_dt.year, 12, 31)

    def _get_report_url(self, format):
        if format == 'xml':
            return "{}/counterXML.php".format(
                self.report_base_url
            )
        if format == 'html':
            return "{}/counterHTML.php".format(
                self.report_base_url
            )
        return self.report_base_url
