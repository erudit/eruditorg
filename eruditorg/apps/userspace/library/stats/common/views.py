import datetime as dt

from django.views.generic import TemplateView

from base.viewmixins import LoginRequiredMixin
from base.viewmixins import MenuItemMixin

from apps.userspace.library.viewmixins import OrganisationScopePermissionRequiredMixin


class StatsLandingView(
        LoginRequiredMixin, MenuItemMixin, OrganisationScopePermissionRequiredMixin, TemplateView):
    menu_library = 'stats'
    permission_required = 'subscription.access_library_stats'
    template_name = 'userspace/library/stats/landing.html'

    def get_context_data(self, **kwargs):
        context = super(StatsLandingView, self).get_context_data(**kwargs)
        current_year = dt.datetime.now().year
        context['years'] = range(current_year, current_year - 20, -1)
        return context
