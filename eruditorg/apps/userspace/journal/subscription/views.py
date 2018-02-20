import csv
import datetime as dt
import logging
import os
import urllib.parse

from account_actions.models import AccountActionToken
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, DeleteView, ListView, View, TemplateView
from django.views.generic.detail import BaseDetailView
from django.views.generic.detail import SingleObjectTemplateResponseMixin

from base.viewmixins import MenuItemMixin
from core.subscription.models import JournalAccessSubscription
from core.subscription.models import JournalManagementSubscription
from core.subscription.shortcuts import get_journal_organisation_subscribers
from core.victor import Victor

from ..viewmixins import JournalScopePermissionRequiredMixin
from ..views import journal_reports_path, BaseReportsDownload

from .forms import JournalAccessSubscriptionCreateForm

logger = logging.getLogger(__name__)


class IndividualJournalAccessSubscriptionListView(
        JournalScopePermissionRequiredMixin, MenuItemMixin, ListView):
    context_object_name = 'subscriptions'
    menu_journal = 'subscription'
    model = JournalAccessSubscription
    paginate_by = 10
    permission_required = 'subscription.manage_institutional_subscription'
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
        JournalScopePermissionRequiredMixin, MenuItemMixin, CreateView):
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
        JournalScopePermissionRequiredMixin, MenuItemMixin, DeleteView):
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
        JournalScopePermissionRequiredMixin, MenuItemMixin, SingleObjectTemplateResponseMixin,
        BaseDetailView):
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


class JournalOrganisationSubscriptionList(
        JournalScopePermissionRequiredMixin, MenuItemMixin, TemplateView):
    menu_journal = 'subscription'
    template_name = 'userspace/journal/subscription/organisationsubscription_list.html'
    permission_required = 'subscription.manage_individual_subscription'
    ARCHIVE_SUBPATH = 'Abonnements/Abonnes'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subscribed_organisations'] = get_journal_organisation_subscribers(
            self.current_journal)
        return context

    def get_subscriptions_archive_years(self):
        thisyear = dt.date.today().year
        root_path = journal_reports_path(self.current_journal.code)
        result = [(str(thisyear), reverse('userspace:journal:subscription:org_export'))]
        try:
            path = os.path.join(root_path, self.ARCHIVE_SUBPATH)
            fns = sorted(os.listdir(path), reverse=True)
            for fn in fns:
                year = os.path.splitext(fn)[0]
                subpath = urllib.parse.quote(os.path.join(self.ARCHIVE_SUBPATH, fn))
                url = reverse('userspace:journal:subscription:org_export_download')
                url += '?subpath={}'.format(subpath)
                result.append((year, url))
        except FileNotFoundError:
            # No archive, just list current year
            pass
        return result


class JournalOrganisationSubscriptionExport(
        JournalScopePermissionRequiredMixin, View):

    permission_required = 'subscription.manage_individual_subscription'

    def get(self, request, *args, **kwargs):
        thisyear = dt.date.today().year
        # It's important to use the latin-1 encoding or else Excel balks at us when comes the time
        # to open the file.
        response = HttpResponse(content_type='text/csv', charset='latin-1')
        response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(thisyear)
        csvwriter = csv.writer(response, delimiter=';')

        # Don't remove spaces around the ID header! otherwise, MS Excel will think that it's a
        # SYLK file. https://www.alunr.com/excel-csv-import-returns-an-sylk-file-format-error/
        csvwriter.writerow([
            ' ID ', 'Nom', 'Adresse', 'Ville', 'Province / État', 'Pays', 'Code postal',
            'Nom du contact', 'Courriel'])

        subscribers = Victor.get_configured_instance().get_subscriber_contact_informations(
            self.current_journal.legacy_code)

        ATTRS = [
            'Id', 'InstitutionName', 'Address', 'City', 'Province', 'Country', 'PostalCode',
            'FullName', 'Email']
        for subscriber in subscribers:
            row = [getattr(subscriber, attrname, '') for attrname in ATTRS]
            # Some characters given to us by Victor aren't in the latin-1 scope.
            row = [str(val).replace('’', '\'') for val in row]
            csvwriter.writerow(row)
        return response


class JournalOrganisationSubscriptionExportDownload(BaseReportsDownload):
    permission_required = 'subscription.manage_individual_subscription'
    AUTHORIZED_SUBPATH = 'Abonnements/Abonnes'
