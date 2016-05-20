# -*- coding: utf-8 -*-

from django.views.generic import ListView

from base.viewmixins import LoginRequiredMixin
from base.viewmixins import MenuItemMixin
from core.subscription.models import InstitutionIPAddressRange

from ..viewmixins import OrganisationScopePermissionRequiredMixin


class InstitutionIPAddressRangeListView(
        LoginRequiredMixin, OrganisationScopePermissionRequiredMixin, MenuItemMixin, ListView):
    context_object_name = 'subscription_ip_ranges'
    menu_library = 'subscription_ips'
    model = InstitutionIPAddressRange
    paginate_by = 10
    permission_required = 'subscription.manage_organisation_subscription_ips'
    template_name = 'userspace/library/subscription_ips/ipaddressrange_list.html'

    def get_queryset(self):
        qs = super(InstitutionIPAddressRangeListView, self).get_queryset()
        return qs.filter(subscription__organisation=self.current_organisation)
