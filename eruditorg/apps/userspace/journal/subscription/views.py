# -*- coding: utf-8 -*-

import logging

from account_actions.models import AccountActionToken
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import ListView
from django.views.generic.detail import BaseDetailView
from django.views.generic.detail import SingleObjectTemplateResponseMixin

from base.viewmixins import LoginRequiredMixin
from base.viewmixins import MenuItemMixin
from core.subscription.models import JournalAccessSubscription
from core.subscription.models import JournalManagementSubscription
from core.subscription.shortcuts import get_journal_organisation_subscribers

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
        context['subscribed_organisations'] = get_journal_organisation_subscribers(
            self.current_journal)
        return context

    def get_queryset(self):
        qs = super(IndividualJournalAccessSubscriptionListView, self).get_queryset()
        journal_management_subscription = JournalManagementSubscription.objects.filter(
            journal=self.current_journal
        ).first()

        return qs.filter(
            user__isnull=False,
            journal_management_subscription=journal_management_subscription
        ).order_by(
            'user__last_name'
        )


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
            if management_subscription.is_full:
                messages.warning(
                    self.request,
                    _("Vous avez épuisé la limite du nombre d'abonnements pour cette revue."))
                return HttpResponseRedirect(
                    reverse('userspace:journal:subscription:list', args=(self.current_journal.pk,)))

            return super(IndividualJournalAccessSubscriptionCreateView, self) \
                .get(request, *args, **kwargs)
        except JournalManagementSubscription.DoesNotExist:  # pragna: no cover
            logger.error(
                'Unable to find the management subscription of the following journal: {}'.format(
                    self.current_journal.name),
                exc_info=True, extra={'request': self.request, })
            messages.warning(
                self.request,
                _("Vous ne pouvez pas gérer les abonnements de votre revue"))
            return HttpResponseRedirect(
                reverse('userspace:journal:subscription:list', args=(self.current_journal.pk,)))

    def get_form_kwargs(self):
        management_subscription = JournalManagementSubscription.objects.get(
            journal=self.current_journal)
        kwargs = super(IndividualJournalAccessSubscriptionCreateView, self).get_form_kwargs()
        kwargs.update({'management_subscription': management_subscription})
        return kwargs

    def get_success_url(self):
        messages.success(self.request, _("L'abonnement a été créé avec succès"))
        return reverse(
            'userspace:journal:subscription:list', args=(self.current_journal.pk, ))


class IndividualJournalAccessSubscriptionDeleteView(
        LoginRequiredMixin, JournalScopePermissionRequiredMixin, MenuItemMixin, DeleteView):
    context_object_name = 'subscription'
    force_scope_switch_to_pattern_name = 'userspace:journal:subscription:list'
    menu_journal = 'subscription'
    model = JournalAccessSubscription
    permission_required = 'subscription.manage_individual_subscription'
    template_name = 'userspace/journal/subscription/individualsubscription_delete.html'

    def get_queryset(self):
        qs = super(IndividualJournalAccessSubscriptionDeleteView, self).get_queryset()
        return qs.filter(journal=self.current_journal)

    def get_success_url(self):
        messages.success(self.request, _("L'abonnement a été supprimé avec succès"))
        return reverse(
            'userspace:journal:subscription:list', args=(self.current_journal.pk, ))


class IndividualJournalAccessSubscriptionCancelView(
        LoginRequiredMixin, JournalScopePermissionRequiredMixin, MenuItemMixin,
        SingleObjectTemplateResponseMixin, BaseDetailView):
    force_scope_switch_to_pattern_name = 'userspace:journal:subscription:list'
    menu_journal = 'subscription'
    model = AccountActionToken
    permission_required = 'subscription.manage_individual_subscription'
    template_name = 'userspace/journal/subscription/individualsubscription_cancel.html'

    def get_queryset(self):
        return AccountActionToken.pending_objects.filter(
            content_type=ContentType.objects.get_for_model(self.current_journal),
            object_id=self.current_journal.id)

    def post(self, request, *args, **kwargs):
        self.request = request
        self.object = self.get_object()
        self.object.cancel()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        messages.success(self.request, _("La proposition d'abonnement a été annulée avec succès"))
        return reverse(
            'userspace:journal:subscription:list', args=(self.current_journal.pk, ))
