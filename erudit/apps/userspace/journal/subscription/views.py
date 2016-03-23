# -*- coding: utf-8 -*-

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import ListView

from base.viewmixins import LoginRequiredMixin
from base.viewmixins import MenuItemMixin
from core.subscription.models import JournalAccessSubscription

from ..viewmixins import JournalScopePermissionRequiredMixin

from .forms import JournalAccessSubscriptionCreateForm


class IndividualJournalAccessSubscriptionListView(
        LoginRequiredMixin, JournalScopePermissionRequiredMixin, MenuItemMixin, ListView):
    context_object_name = 'subscriptions'
    menu_journal = 'subscription'
    model = JournalAccessSubscription
    paginate_by = 10
    permission_required = 'subscription.manage_individual_subscription'
    template_name = 'userspace/journal/subscription/individualsubscription_list.html'

    def get_queryset(self):
        qs = super(IndividualJournalAccessSubscriptionListView, self).get_queryset()
        return qs.filter(user__isnull=False, journal=self.current_journal)


class IndividualJournalAccessSubscriptionCreateView(
        LoginRequiredMixin, JournalScopePermissionRequiredMixin, MenuItemMixin, CreateView):
    form_class = JournalAccessSubscriptionCreateForm
    menu_journal = 'subscription'
    model = JournalAccessSubscription
    permission_required = 'subscription.manage_individual_subscription'
    template_name = 'userspace/journal/subscription/individualsubscription_create.html'

    def get_success_url(self):
        return reverse(
            'userspace:journal:subscription:list', args=(self.current_journal.pk, ))


class IndividualJournalAccessSubscriptionDeleteView(
        LoginRequiredMixin, JournalScopePermissionRequiredMixin, MenuItemMixin, DeleteView):
    context_object_name = 'subscription'
    menu_journal = 'subscription'
    model = JournalAccessSubscription
    permission_required = 'subscription.manage_individual_subscription'
    template_name = 'userspace/journal/subscription/individualsubscription_delete.html'

    def get_success_url(self):
        messages.success(self.request, _("L'abonnement a été supprimé avec succès"))
        return reverse(
            'userspace:journal:subscription:list', args=(self.current_journal.pk, ))
