# -*- coding: utf-8 -*-

from django.urls import reverse

from base.viewmixins import MenuItemMixin
from core.authorization.defaults import AuthorizationConfig as AC

from ...generic_apps.authorization.views import (
    AuthorizationCreateView as BaseAuthorizationCreateView,
)
from ...generic_apps.authorization.views import (
    AuthorizationDeleteView as BaseAuthorizationDeleteView,
)
from ...generic_apps.authorization.views import AuthorizationUserView as BaseAuthorizationUserView

from ..viewmixins import OrganisationScopePermissionRequiredMixin


LIBRARY_AUTHORIZATIONS = [
    AC.can_manage_authorizations,
    AC.can_manage_organisation_subscription_ips,
    AC.can_manage_organisation_members,
]


class AuthorizationUserView(
    OrganisationScopePermissionRequiredMixin, MenuItemMixin, BaseAuthorizationUserView
):
    menu_library = "authorization"
    permission_required = "userspace.staff_access"
    template_name = "userspace/library/authorization/authorization_user.html"

    related_authorizations = LIBRARY_AUTHORIZATIONS

    def get_target_instance(self):
        return self.current_organisation


class AuthorizationCreateView(
    OrganisationScopePermissionRequiredMixin, MenuItemMixin, BaseAuthorizationCreateView
):
    menu_library = "authorization"
    permission_required = "userspace.staff_access"
    template_name = "userspace/library/authorization/authorization_create.html"

    related_authorizations = LIBRARY_AUTHORIZATIONS

    def get_success_url(self):
        return reverse("userspace:library:authorization:list", args=(self.current_organisation.id,))

    def get_target_instance(self):
        return self.current_organisation


class AuthorizationDeleteView(
    OrganisationScopePermissionRequiredMixin, MenuItemMixin, BaseAuthorizationDeleteView
):
    force_scope_switch_to_pattern_name = "userspace:library:authorization:list"
    menu_library = "authorization"
    permission_required = "userspace.staff_access"
    template_name = "userspace/library/authorization/authorization_confirm_delete.html"

    def get_permission_object(self):
        authorization = self.get_object()
        return authorization.content_object

    def get_success_url(self):
        return reverse("userspace:library:authorization:list", args=(self.current_organisation.id,))

    def get_target_instance(self):
        return self.current_organisation
