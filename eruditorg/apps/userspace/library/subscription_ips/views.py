# -*- coding: utf-8 -*-

from django.contrib import messages
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import ListView

from django.contrib.auth.mixins import LoginRequiredMixin
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
    permission_required = 'library.has_access_to_dashboard'
    template_name = 'userspace/library/subscription_ips/ipaddressrange_list.html'

    def get_queryset(self):
        qs = super(InstitutionIPAddressRangeListView, self).get_queryset()
        return qs.filter(subscription__organisation=self.current_organisation).order_by('pk')


class InstitutionIPAddressRangeCreateView(
        LoginRequiredMixin, OrganisationScopePermissionRequiredMixin, MenuItemMixin, CreateView):
    form_class = InstitutionIPAddressRangeForm
    menu_library = 'subscription_ips'
    model = InstitutionIPAddressRange
    permission_required = 'userspace.staff_access'
    template_name = 'userspace/library/subscription_ips/ipaddressrange_create.html'

    def get_form_kwargs(self):
        kwargs = super(InstitutionIPAddressRangeCreateView, self).get_form_kwargs()
        kwargs.update({'subscription': self.get_current_subscription()})
        return kwargs

    def get_current_subscription(self):
        return JournalAccessSubscription.valid_objects.filter(
            organisation=self.current_organisation).first()

    def get_success_url(self):
        messages.success(self.request, _("La plage d’adresses IP a été créée avec succès."))
        return reverse(
            'userspace:library:subscription_ips:list', args=(self.current_organisation.pk, ))


class InstitutionIPAddressRangeDeleteView(
        LoginRequiredMixin, OrganisationScopePermissionRequiredMixin, MenuItemMixin, DeleteView):
    context_object_name = 'ip_range'
    force_scope_switch_to_pattern_name = 'userspace:library:subscription_ips:list'
    menu_library = 'subscription_ips'
    model = InstitutionIPAddressRange
    permission_required = 'userspace.staff_access'
    template_name = 'userspace/library/subscription_ips/ipaddressrange_delete.html'

    def get_queryset(self):
        qs = super(InstitutionIPAddressRangeDeleteView, self).get_queryset()
        return qs.filter(subscription__organisation=self.current_organisation)

    def get_success_url(self):
        messages.success(self.request, _("La plage d’adresses IP a été supprimée avec succès."))
        return reverse(
            'userspace:library:subscription_ips:list', args=(self.current_organisation.id, ))
