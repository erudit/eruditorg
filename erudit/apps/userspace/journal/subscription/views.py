# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import ListView
from django.views.generic import UpdateView

from base.viewmixins import LoginRequiredMixin
from base.viewmixins import MenuItemMixin
from core.subscription.models import JournalAccessSubscription

from ..viewmixins import JournalScopePermissionRequiredMixin

from .forms import JournalAccessSubscriptionForm


class IndividualJournalAccessSubscriptionListView(
        LoginRequiredMixin, JournalScopePermissionRequiredMixin, MenuItemMixin, ListView):
    menu_journal = 'subscription'
    model = JournalAccessSubscription
    paginate_by = 10
    permission_required = 'subscription.manage_individual_subscription'
    template_name = 'userspace/journal/subscription/individualaccount_filter.html'

    def get_queryset(self):
        qs = super(IndividualJournalAccessSubscriptionListView, self).get_queryset()
        return qs.filter(journal=self.current_journal)


class IndividualJournalAccessSubscriptionCreateView(
        LoginRequiredMixin, JournalScopePermissionRequiredMixin, MenuItemMixin, CreateView):
    form_class = JournalAccessSubscriptionForm
    menu_journal = 'subscription'
    model = JournalAccessSubscription
    permission_required = 'subscription.manage_individual_subscription'
    template_name = 'userspace/journal/subscription/individualaccount_create.html'

    def get_success_url(self):
        return reverse(
            'userspace:journal:subscription:account_list', args=(self.current_journal.pk, ))

    def get_form_kwargs(self):
        kwargs = super(IndividualJournalAccessSubscriptionCreateView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs


class IndividualJournalAccessSubscriptionUpdateView(
        LoginRequiredMixin, JournalScopePermissionRequiredMixin, MenuItemMixin, UpdateView):
    form_class = JournalAccessSubscriptionForm
    menu_journal = 'subscription'
    model = JournalAccessSubscription
    permission_required = 'subscription.manage_individual_subscription'
    template_name = 'userspace/journal/subscription/individualaccount_update.html'

    def get_form_kwargs(self):
        kwargs = super(IndividualJournalAccessSubscriptionUpdateView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_success_url(self):
        return reverse(
            'userspace:journal:subscription:account_list', args=(self.current_journal.pk, ))


class IndividualJournalAccessSubscriptionDeleteView(
        LoginRequiredMixin, JournalScopePermissionRequiredMixin, MenuItemMixin, DeleteView):
    menu_journal = 'subscription'
    model = JournalAccessSubscription
    permission_required = 'subscription.manage_individual_subscription'
    template_name = 'userspace/journal/subscription/individualaccount_confirm_delete.html'

    def get_success_url(self):
        return reverse(
            'userspace:journal:subscription:account_list', args=(self.current_journal.pk, ))
