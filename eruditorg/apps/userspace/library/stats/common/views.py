import datetime as dt

from django.views.generic import TemplateView
from django.utils.translation import gettext as _

from django.contrib.auth.mixins import LoginRequiredMixin
from base.viewmixins import MenuItemMixin

from apps.userspace.library.viewmixins import OrganisationScopePermissionRequiredMixin


class StatsLandingView(
    LoginRequiredMixin, MenuItemMixin, OrganisationScopePermissionRequiredMixin, TemplateView
):
    menu_library = "stats"
    permission_required = "subscription.access_library_stats"
    template_name = "userspace/library/stats/landing.html"

    def get_context_data(self, **kwargs):
        context = super(StatsLandingView, self).get_context_data(**kwargs)
        current_year = dt.datetime.now().year
        context["years"] = range(current_year, current_year - 20, -1)
        months = []
        for month in range(1, 13):
            month_date = dt.date(current_year, month, 1)

            months.append((month, _(month_date.strftime("%B"))))
        context["months"] = months
        return context
