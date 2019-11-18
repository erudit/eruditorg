import datetime
import json
import requests

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from django.conf import settings

from base.viewmixins import MenuItemMixin

from ..viewmixins import OrganisationScopePermissionRequiredMixin


class CollectionView(
        LoginRequiredMixin, MenuItemMixin, OrganisationScopePermissionRequiredMixin, TemplateView):
    menu_library = 'collection'
    permission_required = 'library.has_access_to_dashboard'
    template_name = 'userspace/library/collection/landing.html'

    def get_target_instance(self):
        return self.current_organisation

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if settings.ABONNEMENTS_BASKETS_BACKEND_URL is None:
            return context
        response = requests.get(
            settings.ABONNEMENTS_BASKETS_BACKEND_URL + str(datetime.datetime.now().year),
        )
        if response.status_code == 200:
            context['baskets'] = json.loads(response.content.decode())
            context['kbart_2014_backend_url'] = settings.KBART_2014_BACKEND_URL
        return context
