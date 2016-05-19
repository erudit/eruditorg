# -*- coding: utf-8 -*-

from base.viewmixins import MenuItemMixin
from core.authorization.defaults import AuthorizationConfig as AC
from core.subscription.models import JournalManagementSubscription

from ...generic_apps.authorization.views import AuthorizationCreateView \
    as BaseAuthorizationCreateView
from ...generic_apps.authorization.views import AuthorizationDeleteView \
    as BaseAuthorizationDeleteView
from ...generic_apps.authorization.views import AuthorizationUserView as BaseAuthorizationUserView

from ..viewmixins import JournalScopePermissionRequiredMixin


class AuthorizationUserView(
        JournalScopePermissionRequiredMixin, MenuItemMixin, BaseAuthorizationUserView):
    menu_journal = 'authorization'
    permission_required = 'authorization.manage_authorizations'
    template_name = 'userspace/journal/authorization/authorization_user.html'

    def get_authorizations_per_app(self):
        data = super(AuthorizationUserView, self).get_authorizations_per_app()

        # Special case: the subscription authorizations cannot be granted if the current journal
        # is not associated with a management plan.
        if AC.can_manage_individual_subscription.codename in data:
            if not JournalManagementSubscription.objects.filter(journal=self.current_journal) \
                    .exists():
                data.pop(AC.can_manage_individual_subscription.codename)

        return data


class AuthorizationCreateView(
        JournalScopePermissionRequiredMixin, MenuItemMixin, BaseAuthorizationCreateView):
    menu_journal = 'authorization'
    permission_required = 'authorization.manage_authorizations'
    template_name = 'userspace/journal/authorization/authorization_create.html'

    def has_permission(self):
        has_perm = super(AuthorizationCreateView, self).has_permission()
        auth_codename = self.authorization_definition[0]
        if has_perm and auth_codename == AC.can_manage_individual_subscription.codename \
                and not JournalManagementSubscription.objects.filter(
                    journal=self.current_journal).exists():
            return False
        return has_perm


class AuthorizationDeleteView(
        JournalScopePermissionRequiredMixin, MenuItemMixin, BaseAuthorizationDeleteView):
    menu_journal = 'authorization'
    permission_required = 'authorization.manage_authorizations'
    template_name = 'userspace/journal/authorization/authorization_confirm_delete.html'

    def get_permission_object(self):
        authorization = self.get_object()
        return authorization.content_object
