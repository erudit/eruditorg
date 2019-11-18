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
