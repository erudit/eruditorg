# -*- coding: utf-8 -*-

import datetime as dt

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import ListView

from base.viewmixins import LoginRequiredMixin
from base.viewmixins import MenuItemMixin
from core.subscription.models import InstitutionIPAddressRange
from core.subscription.models import JournalAccessSubscription

from ..viewmixins import OrganisationScopePermissionRequiredMixin

from .forms import InstitutionIPAddressRangeForm


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


class InstitutionIPAddressRangeCreateView(
        LoginRequiredMixin, OrganisationScopePermissionRequiredMixin, MenuItemMixin, CreateView):
    form_class = InstitutionIPAddressRangeForm
    menu_library = 'subscription_ips'
    model = InstitutionIPAddressRange
    permission_required = 'subscription.manage_organisation_subscription_ips'
    template_name = 'userspace/library/subscription_ips/ipaddressrange_create.html'

    def get_form_kwargs(self):
        kwargs = super(InstitutionIPAddressRangeCreateView, self).get_form_kwargs()
        kwargs.update({'subscription': self.get_current_subscription()})
        return kwargs

    def get_current_subscription(self):
        nowd = dt.datetime.now().date()
        return JournalAccessSubscription.objects.filter(
            organisation=self.current_organisation,
            journalaccesssubscriptionperiod__start__lte=nowd,
            journalaccesssubscriptionperiod__end__gte=nowd).first()

    def get_success_url(self):
        messages.success(self.request, _("La plage d'adresse IP a été créée avec succès"))
        return reverse(
            'userspace:library:subscription_ips:list', args=(self.current_organisation.pk, ))


class InstitutionIPAddressRangeDeleteView(
        LoginRequiredMixin, OrganisationScopePermissionRequiredMixin, MenuItemMixin, DeleteView):
    context_object_name = 'ip_range'
    menu_library = 'subscription_ips'
    model = InstitutionIPAddressRange
    permission_required = 'subscription.manage_organisation_subscription_ips'
    template_name = 'userspace/library/subscription_ips/ipaddressrange_delete.html'

    def get_success_url(self):
        messages.success(self.request, _("La plage d'adresse IP a été supprimée avec succès"))
        return reverse(
            'userspace:library:subscription_ips:list', args=(self.current_organisation.id, ))
