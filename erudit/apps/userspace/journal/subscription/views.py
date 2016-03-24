# -*- coding: utf-8 -*-

import logging

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import ListView

from base.viewmixins import LoginRequiredMixin
from base.viewmixins import MenuItemMixin
from core.account_actions.models import AccountActionToken
from core.subscription.models import JournalAccessSubscription
from core.subscription.models import JournalManagementSubscription

from ..viewmixins import JournalScopePermissionRequiredMixin

from .forms import JournalAccessSubscriptionCreateForm

logger = logging.getLogger(__name__)


class IndividualJournalAccessSubscriptionListView(
        LoginRequiredMixin, JournalScopePermissionRequiredMixin, MenuItemMixin, ListView):
    context_object_name = 'subscriptions'
    menu_journal = 'subscription'
    model = JournalAccessSubscription
    paginate_by = 10
    permission_required = 'subscription.manage_individual_subscription'
    template_name = 'userspace/journal/subscription/individualsubscription_list.html'

    def get_context_data(self, **kwargs):
        context = super(IndividualJournalAccessSubscriptionListView, self) \
            .get_context_data(**kwargs)
        context['pending_subscriptions'] = AccountActionToken.pending_objects \
            .get_for_object(self.current_journal)
        return context

    def get_queryset(self):
        qs = super(IndividualJournalAccessSubscriptionListView, self).get_queryset()
        return qs.filter(user__isnull=False, journal=self.current_journal)


class IndividualJournalAccessSubscriptionCreateView(
        LoginRequiredMixin, JournalScopePermissionRequiredMixin, MenuItemMixin, CreateView):
    form_class = JournalAccessSubscriptionCreateForm
    menu_journal = 'subscription'
    model = AccountActionToken  # We create an AccountActionToken instance in this view.
    permission_required = 'subscription.manage_individual_subscription'
    template_name = 'userspace/journal/subscription/individualsubscription_create.html'

    def get(self, request, *args, **kwargs):
        try:
            management_subscription = JournalManagementSubscription.objects.get(
                journal=self.current_journal)
        except JournalManagementSubscription.DoesNotExist:  # pragna: no cover
            plan_consumed = False
            logger.error(
                'Unable to find the management subscription of the following journal: {}'.format(
                    self.current_journal.name),
                exc_info=True, extra={'request': self.request, })
        else:
            subscriptions = JournalAccessSubscription.objects.filter(
                user__isnull=False, journal=self.current_journal)
            pending = AccountActionToken.pending_objects \
                .get_for_object(self.current_journal)
            consumed = AccountActionToken.consumed_objects \
                .get_for_object(self.current_journal)
            total_subscriptions = subscriptions.count() + pending.count() + consumed.count()
            plan_consumed = total_subscriptions >= management_subscription.plan.max_accounts

        if plan_consumed:
            messages.warning(
                self.request,
                _("Vous avez épuisé la limite du nombre d'abonnements pour cette revue."))
            return HttpResponseRedirect(
                reverse('userspace:journal:subscription:list', args=(self.current_journal.pk, )))

        return super(IndividualJournalAccessSubscriptionCreateView, self) \
            .get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(IndividualJournalAccessSubscriptionCreateView, self).get_form_kwargs()
        kwargs.update({'journal': self.current_journal})
        return kwargs

    def get_success_url(self):
        messages.success(self.request, _("L'abonnement a été créé avec succès"))
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
