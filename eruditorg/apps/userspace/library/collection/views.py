# -*- coding: utf-8 -*-

from base.viewmixins import MenuItemMixin

from ...generic_apps.authorization.views import AuthorizationUserView as BaseAuthorizationUserView

from ..viewmixins import OrganisationScopePermissionRequiredMixin


class CollectionView(
        OrganisationScopePermissionRequiredMixin, MenuItemMixin, BaseAuthorizationUserView):
    menu_library = 'collection'
    permission_required = 'subscription.collection'
    template_name = 'userspace/library/collection/landing.html'

    def get_target_instance(self):
        return self.current_organisation
