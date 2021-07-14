import datetime as dt
from functools import singledispatch
from io import TextIOWrapper
from tempfile import TemporaryFile
from typing import Type, Tuple

import requests
from django.conf import settings

from django.http import (
    HttpResponse,
    FileResponse,
)
from django.views.generic import TemplateView

from erudit.models import Organisation

from django.contrib.auth.mixins import LoginRequiredMixin
from base.viewmixins import MenuItemMixin

from apps.public.site_messages.models import SiteMessage
from apps.userspace.library.viewmixins import OrganisationScopePermissionRequiredMixin

from .forms import (
    CounterReportForm,
    REPORT_FORMS,
    CounterR4Form,
    CounterR5Form,
    DatesRange,
)

from counter_r5 import CounterR5Report, CounterR5Config


def compute_r4_end_month(today: dt.date) -> dt.date:
    # first day of the previous month
    return (today.replace(day=1) - dt.timedelta(days=1)).replace(day=1)


def get_stats_form(
    form_class: Type[CounterReportForm],
    request_data: dict,
    available_range: DatesRange,
) -> Tuple[CounterReportForm, bool]:
    """Create a counter report request form and initialize it if it has been submitted."""

    # There is one form for each type for counter report, but only one can be submitted at a time.
    # If this form was submitted then the submit button name will be in the HTTP GET request's data.
    is_submitted = form_class.submit_name() in request_data
    kwargs = {
        "data": request_data if is_submitted else None,
    }
    return form_class(available_range, **kwargs), is_submitted


# noinspection PyUnusedLocal
@singledispatch
def get_report_response(form: CounterReportForm, organisation: Organisation) -> HttpResponse:
    """Generate a HTTP Response containing the Counter report data requested in the submitted
    form for the current organization.

    """
    pass


@get_report_response.register(CounterR4Form)
def get_r4_report_response(form: CounterR4Form, organisation: Organisation) -> HttpResponse:
    dstart, dend = form.get_report_period()
    report_arguments = {
        "format": form.cleaned_data["format"],
        "id": organisation.account_id,
        "beginPeriod": dstart.strftime("%Y-%m-%d"),
        "endPeriod": dend.strftime("%Y-%m-%d"),
    }
    if form.is_gold_open_access:
        report_arguments["isGoldOpenAccess"] = True
    # by default, the format is CSV
    report_format = report_arguments["format"]
    url = settings.ERUDIT_COUNTER_BACKEND_URL
    if report_format == "xml":
        url = f"{url}/counterXML.php"
    elif report_format == "html":
        url = f"{url}/counterHTML.php"
    report = requests.get(url, params=report_arguments)
    filename = "{id}-{beginPeriod}-{endPeriod}".format(**report_arguments)
    response = HttpResponse(report, content_type=f"application/{report_format}")
    response["Content-Disposition"] = f'attachment; filename="{filename}.{report_format}"'
    return response


@get_report_response.register(CounterR5Form)
def get_r5_report_response(form: CounterR5Form, organisation: Organisation) -> FileResponse:
    begin_date, end_date = form.get_report_period()
    organisation_id = organisation.account_id
    config = get_counter_r5_config()
    report = CounterR5Report(
        config=config,
        report_type=form.report_code,
        customer_id=organisation.account_id,
        customer_name=organisation.name,
        begin_date=begin_date,
        end_date=end_date,
    )

    f = TemporaryFile("w+b")
    try:
        # csv writers in R5 library want a text file, but FileResponse wants a binary file
        # so the binary temp file is wrapped in a TextIOWrapper that does the conversion.
        # `newline=""`, as asked by the csv module, and `write_through=False` because
        # additional buffering is not needed in this case
        text_wrapper = TextIOWrapper(f, encoding="utf-8-sig", newline="", write_through=True)
        report.write_csv(text_wrapper)
        # if not detached, TextIOWrapper would close the file when destroyed (ie. when it goes
        # out of scope)
        text_wrapper.detach()
        f.seek(0)
        response = FileResponse(f, content_type="application/csv; charset=utf-8-sig")
        filename = (
            f"{form.report_code}-{organisation_id}-"
            f"{begin_date.strftime('%Y-%m-%d')}-{end_date.strftime('%Y-%m-%d')}"
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
        return response
    except Exception:
        # if there is no exception, then the tempfile will be closed (and deleted) by
        # ``FileResponse``.
        f.close()
        raise


def get_counter_r5_config():
    return CounterR5Config(
        first_available_month=dt.datetime.strptime(
            settings.COUNTER_R5_FIRST_AVAILABLE_MONTH, "%Y-%m-%d"
        ).date(),
        available_after=settings.COUNTER_R5_AVAILABLE_AFTER,
        es_index=settings.ELASTICSEARCH_STATS_INDEX,
        es_host=settings.ELASTICSEARCH_STATS_HOST,
        es_port=settings.ELASTICSEARCH_STATS_PORT,
        global_filters={"audit.is_legitimate": True},
    )


class StatsLandingView(
    LoginRequiredMixin, MenuItemMixin, OrganisationScopePermissionRequiredMixin, TemplateView
):

    menu_library = "stats"
    permission_required = "library.has_access_to_dashboard"
    template_name = "userspace/library/stats/landing.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        submitted_form = context.get("submitted_form", None)
        if submitted_form and submitted_form.is_valid():
            return get_report_response(submitted_form, self.current_organisation)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(StatsLandingView, self).get_context_data(**kwargs)
        today = dt.date.today()
        r5_config = get_counter_r5_config()

        available_ranges = {
            "R4": DatesRange(dt.date(2010, 1, 1), compute_r4_end_month(today)),
            "R5": DatesRange(
                r5_config.first_available_month, r5_config.get_last_available_month(today)
            ),
        }
        context["forms"] = {
            "R4": [],
            "R5": [],
        }
        for form_class in REPORT_FORMS:
            available_range = available_ranges[form_class.counter_release]
            form, is_submitted = get_stats_form(form_class, self.request.GET, available_range)
            context["forms"][form.counter_release].append(form)
            if is_submitted:
                context["submitted_form"] = form
        context["section_aside"] = True
        context["library_statistics_site_messages"] = SiteMessage.objects.library_statistics()
        return context
