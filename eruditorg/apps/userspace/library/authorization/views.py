# -*- coding: utf-8 -*-

from base.viewmixins import MenuItemMixin

from ...generic_apps.authorization.views import AuthorizationCreateView \
    as BaseAuthorizationCreateView
from ...generic_apps.authorization.views import AuthorizationDeleteView \
    as BaseAuthorizationDeleteView
from ...generic_apps.authorization.views import AuthorizationUserView as BaseAuthorizationUserView

from ..viewmixins import OrganisationScopePermissionRequiredMixin


class AuthorizationUserView(
        OrganisationScopePermissionRequiredMixin, MenuItemMixin, BaseAuthorizationUserView):
    library_journal = 'authorization'
    permission_required = 'authorization.manage_authorizations'
    template_name = 'userspace/library/authorization/authorization_user.html'


class AuthorizationCreateView(
        OrganisationScopePermissionRequiredMixin, MenuItemMixin, BaseAuthorizationCreateView):
    library_journal = 'authorization'
    permission_required = 'authorization.manage_authorizations'
    template_name = 'userspace/library/authorization/authorization_create.html'


class AuthorizationDeleteView(
        OrganisationScopePermissionRequiredMixin, MenuItemMixin, BaseAuthorizationDeleteView):
    library_journal = 'authorization'
    permission_required = 'authorization.manage_authorizations'
    template_name = 'userspace/library/authorization/authorization_confirm_delete.html'

    def get_permission_object(self):
        authorization = self.get_object()
        return authorization.content_object
