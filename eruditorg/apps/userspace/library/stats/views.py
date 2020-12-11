# -*- coding: utf-8 -*-
import datetime as dt
import typing
from io import StringIO

import requests
from django.conf import settings

from django.http import HttpResponse
from django.views.generic import TemplateView

from apps.userspace.library.shortcuts import get_last_year_of_subscription
from .settings import ERUDIT_COUNTER_BACKEND_URL

from django.contrib.auth.mixins import LoginRequiredMixin
from base.viewmixins import MenuItemMixin

from apps.public.site_messages.models import SiteMessage
from apps.userspace.library.viewmixins import OrganisationScopePermissionRequiredMixin

from .forms import (
    CounterReportForm,
    StatsFormInfo,
    STATS_FORMS_INFO,
    CounterJR1Form,
    CounterJR1GOAForm,
)

from counter_r5.generate import CounterR5Report


def compute_end_year(current_year: int, last_year_of_subscription: typing.Optional[int]) -> int:
    if last_year_of_subscription is None:
        return current_year
    elif last_year_of_subscription <= current_year:
        return last_year_of_subscription

    return current_year


def get_stats_form(
    form_info: StatsFormInfo, request_data: dict, end_year: int
) -> typing.Tuple[CounterReportForm, bool]:
    is_submitted = form_info.submit_name in request_data
    kwargs = {
        "data": request_data if is_submitted else None,
        "form_info": form_info,
        "end_year": end_year,
    }
    return form_info.form_class(**kwargs), is_submitted


class StatsLandingView(
    LoginRequiredMixin, MenuItemMixin, OrganisationScopePermissionRequiredMixin, TemplateView
):

    menu_library = "stats"
    permission_required = "library.has_access_to_dashboard"
    template_name = "userspace/library/stats/landing.html"
    report_base_url = ERUDIT_COUNTER_BACKEND_URL
    counter_jr1_form = CounterJR1Form
    counter_jr1goa_form = CounterJR1GOAForm

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        submitted_form = context.get("submitted_form", None)
        if submitted_form and submitted_form.is_valid():
            # Get the report
            if submitted_form.release == "R4":
                report = self.get_r4_report(submitted_form)
            else:
                report = self.get_r5_report(submitted_form)
            return report

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(StatsLandingView, self).get_context_data(**kwargs)
        current_year = dt.datetime.now().year
        last_year_of_subscription = get_last_year_of_subscription(self.current_organisation)
        end_year = compute_end_year(current_year, last_year_of_subscription)
        forms = []
        for form_info in STATS_FORMS_INFO:
            form, is_submitted = get_stats_form(form_info, self.request.GET, end_year)
            forms.append(form)
            if is_submitted:
                context["submitted_form"] = form
        submitted_form = context.get("submitted_form", None)
        submitted_release = submitted_form.release if submitted_form else None
        releases = {}
        for release in ("R4", "R5"):
            release_forms = [f for f in forms if f.release == release]
            releases[release] = {
                "forms": release_forms,
                "active_form": submitted_form if submitted_release == release else release_forms[0],
            }
        context["releases"] = releases
        context["section_aside"] = True
        context["library_statistics_site_messages"] = SiteMessage.objects.library_statistics()
        return context

    def get_r4_report(self, form):
        dstart, dend = form.get_report_period()
        # report_arguments = form_data
        report_arguments = {
            "format": form.cleaned_data["format"],
            "id": self.get_organisation_id(),
            "beginPeriod": dstart.strftime("%Y-%m-%d"),
            "endPeriod": dend.strftime("%Y-%m-%d"),
        }

        if form.cleaned_data["report_type"] == "counter-jr1-goa":
            report_arguments["isGoldOpenAccess"] = True

        report_format = report_arguments["format"]
        url = self.report_base_url
        if report_format == "xml":
            url = "{}/counterXML.php".format(url)
        elif report_format == "html":
            url = "{}/counterHTML.php".format(url)
        report = requests.get(url, params=report_arguments)
        filename = "{id}-{beginPeriod}-{endPeriod}".format(**report_arguments)
        response = HttpResponse(report, content_type="application/{}".format(report_format))
        response["Content-Disposition"] = 'attachment; filename="{filename}.{format}"'.format(
            filename=filename, format=report_format
        )
        return response

    def get_requested_report(self):
        report_type = None
        if self.request.GET.get("{}-report_type".format(self.counter_jr1_form.prefix)):
            report_type = "counter-jr1"
        elif self.request.GET.get("{}-report_type".format(self.counter_jr1goa_form.prefix)):
            report_type = "counter-jr1-goa"
        return report_type

    def get_report(self, form_data):
        dstart, dend = self.get_report_period(form_data)
        # report_arguments = form_data
        report_arguments = {}
        report_arguments["format"] = form_data["format"]
        report_arguments["id"] = self.current_organisation.account_id
        report_arguments["beginPeriod"] = dstart.strftime("%Y-%m-%d")
        report_arguments["endPeriod"] = dend.strftime("%Y-%m-%d")
        if form_data.get("report_type") == "counter-jr1-goa":
            report_arguments["isGoldOpenAccess"] = True

        format = report_arguments["format"]
        report = requests.get(self._get_report_url(format), params=report_arguments)
        filename = "{id}-{beginPeriod}-{endPeriod}".format(**report_arguments)
        response = HttpResponse(
            report, content_type="application/{format}".format(**report_arguments)
        )
        response["Content-Disposition"] = 'attachment; filename="{filename}.{format}"'.format(
            filename=filename, format=format
        )
        return response

    def get_report_period(self, form_data):
        """ Returns a tuple (start date, end date) containing the period of the report. """
        now_dt = dt.datetime.now()
        year = form_data.get("year", None)
        month_start = form_data.get("month_start", None)
        month_end = form_data.get("month_end", None)
        year_start = form_data.get("year_start", None)
        year_end = form_data.get("year_end", None)

        # First handles the case where a precise period has been specified
        try:
            dstart_str = "{year}-{month}-01".format(year=year_start, month=month_start)
            dstart = dt.datetime.strptime(dstart_str, "%Y-%m-%d").date()
            dend_str = "{year}-{month}-01".format(year=year_end, month=month_end)
            dend = dt.datetime.strptime(dend_str, "%Y-%m-%d").date()
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
        if format == "xml":
            return "{}/counterXML.php".format(self.report_base_url)
        if format == "html":
            return "{}/counterHTML.php".format(self.report_base_url)
        return self.report_base_url

    def get_organisation_id(self):
        return self.current_organisation.account_id

    def get_r5_report(self, form):
        begin_date, end_date = form.get_report_period()
        organisation_id = self.get_organisation_id()
        report = CounterR5Report(
            report_type=form.report_code,
            customer_id=organisation_id,
            customer_name=self.current_organisation.name,
            es_index=settings.ELASTICSEARCH_STATS_INDEX,
            es_host=settings.ELASTICSEARCH_STATS_HOST,
            es_port=settings.ELASTICSEARCH_STATS_PORT,
            begin_date=begin_date,
            end_date=end_date,
            global_filters={"audit.is_legitimate": True},
        )

        f = StringIO()
        report.write_csv(f)
        response = HttpResponse(f.getvalue(), content_type="application/csv")
        filename = "{}-{}-{}".format(
            organisation_id, begin_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
        return response
