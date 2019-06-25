import datetime as dt
import typing

import requests

from django.http import HttpResponse
from django.views.generic import TemplateView

from apps.userspace.library.shortcuts import get_last_year_of_subscription
from .settings import ERUDIT_COUNTER_BACKEND_URL

from django.contrib.auth.mixins import LoginRequiredMixin
from base.viewmixins import MenuItemMixin

from apps.userspace.library.viewmixins import OrganisationScopePermissionRequiredMixin

from .forms import (
    CounterReportForm,
    StatsFormInfo,
    STATS_FORMS_INFO,
)


def compute_end_year(current_year: int, last_year_of_subscription: typing.Optional[int]) -> int:
    if last_year_of_subscription is None:
        return current_year
    elif last_year_of_subscription <= current_year:
        return last_year_of_subscription

    return current_year


def get_stats_form(form_info: StatsFormInfo, request_data: dict,
                   end_year: int) -> typing.Tuple[CounterReportForm, bool]:
    is_submitted = form_info.submit_name in request_data
    kwargs = {
        'data': request_data if is_submitted else None,
        'form_info': form_info,
        'end_year': end_year,
    }
    return form_info.form_class(**kwargs), is_submitted


class StatsLandingView(
        LoginRequiredMixin, MenuItemMixin, OrganisationScopePermissionRequiredMixin, TemplateView):

    menu_library = 'stats'
    permission_required = 'library.has_access_to_dashboard'
    template_name = 'userspace/library/stats/landing.html'
    report_base_url = ERUDIT_COUNTER_BACKEND_URL

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        submitted_form = context.get('submitted_form', None)
        if submitted_form and submitted_form.is_valid():
            # Get the report
            report = self.get_report(submitted_form)
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
                context['submitted_form'] = form
        submitted_form = context.get('submitted_form', None)
        submitted_release = submitted_form.release if submitted_form else None
        releases = {}
        for release in ('R4', 'R5'):
            release_forms = [f for f in forms if f.release == release]
            releases[release] = {
                'forms': release_forms,
                'active_form': submitted_form if submitted_release == release else release_forms[0]
            }
        context['releases'] = releases
        return context

    def get_report(self, form):
        dstart, dend = form.get_report_period()
        # report_arguments = form_data
        report_arguments = {'format': form.cleaned_data['format'],
                            'id': self.current_organisation.legacyorganisationprofile.account_id,
                            'beginPeriod': dstart.strftime("%Y-%m-%d"),
                            'endPeriod': dend.strftime("%Y-%m-%d")}

        if form.cleaned_data['report_type'] == 'counter-jr1-goa':
            report_arguments['isGoldOpenAccess'] = True

        report_format = report_arguments['format']
        report = requests.get(self._get_report_url(report_format), params=report_arguments)
        filename = "{id}-{beginPeriod}-{endPeriod}".format(**report_arguments)
        response = HttpResponse(
            report, content_type="application/{format}".format(**report_arguments)
        )
        response['Content-Disposition'] = 'attachment; filename="{filename}.{format}"'.format(
            filename=filename, format=report_format
        )
        return response

    def _get_report_url(self, report_format):
        if report_format == 'xml':
            return "{}/counterXML.php".format(
                self.report_base_url
            )
        if report_format == 'html':
            return "{}/counterHTML.php".format(
                self.report_base_url
            )
        return self.report_base_url
