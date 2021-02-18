from django.conf import settings

from django.views.generic import TemplateView

from django.contrib.auth.mixins import LoginRequiredMixin
from base.viewmixins import MenuItemMixin

from ..viewmixins import OrganisationScopePermissionRequiredMixin


class ConnectionLandingView(
    LoginRequiredMixin, MenuItemMixin, OrganisationScopePermissionRequiredMixin, TemplateView
):
    menu_library = "connection"
    permission_required = "library.has_access_to_dashboard"
    template_name = "userspace/library/connection/landing.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sushi_requester_id"] = self.current_organisation.sushi_requester_id
        context["id_client"] = self.current_organisation.account_id
        context["sushi_url"] = getattr(settings, "SUSHI_URL", "")
        context["z3950_host"] = getattr(settings, "Z3950_HOST", "")
        context["z3950_port"] = getattr(settings, "Z3950_PORT", "")
        context["z3950_database"] = getattr(settings, "Z3950_DATABASE", "")
        return context
