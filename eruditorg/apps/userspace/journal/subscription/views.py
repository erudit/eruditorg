import csv
import datetime as dt
import io
import structlog
import os
import urllib.parse
import chardet

from account_actions.models import AccountActionToken
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import EmailValidator
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.translation import ugettext as _, ngettext
from django.views.generic import CreateView, DeleteView, ListView, View, TemplateView
from django.views.generic.detail import BaseDetailView
from django.views.generic.detail import SingleObjectTemplateResponseMixin

from base.viewmixins import MenuItemMixin
from core.subscription.account_actions import IndividualSubscriptionAction
from core.subscription.models import JournalAccessSubscription
from core.subscription.models import JournalManagementSubscription
from core.victor import Victor

from ..viewmixins import JournalScopePermissionRequiredMixin
from ..views import journal_reports_path, BaseReportsDownload

from .forms import JournalAccessSubscriptionCreateForm

logger = structlog.getLogger(__name__)


class JournalSubscriptionMixin(JournalScopePermissionRequiredMixin, MenuItemMixin):
    menu_journal = 'subscription'
    permission_required = 'subscription.manage_individual_subscription'
    is_org_view = False


class IndividualJournalAccessSubscriptionListView(JournalSubscriptionMixin, ListView):
    context_object_name = 'subscriptions'
    model = JournalAccessSubscription
    paginate_by = 10
    template_name = 'userspace/journal/subscription/individualsubscription_list.html'

    def get_context_data(self, **kwargs):
        context = super(IndividualJournalAccessSubscriptionListView, self) \
            .get_context_data(**kwargs)
        context['pending_subscriptions'] = AccountActionToken.pending_objects \
            .get_for_object(self.current_journal)
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        journal_management_subscription = JournalManagementSubscription.objects.filter(
            journal=self.current_journal
        ).first()

        return qs.filter(
            user__isnull=False,
            journal_management_subscription=journal_management_subscription
        ).order_by(
            'user__last_name'
        )


class IndividualJournalAccessSubscriptionCreateView(JournalSubscriptionMixin, CreateView):
    form_class = JournalAccessSubscriptionCreateForm
    model = AccountActionToken  # We create an AccountActionToken instance in this view.
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
        except JournalManagementSubscription.DoesNotExist:  # pragma: no cover
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


class IndividualJournalAccessSubscriptionDeleteView(JournalSubscriptionMixin, DeleteView):
    context_object_name = 'subscription'
    force_scope_switch_to_pattern_name = 'userspace:journal:subscription:list'
    model = JournalAccessSubscription
    template_name = 'userspace/journal/subscription/individualsubscription_delete.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(journal_management_subscription__journal=self.current_journal)

    def get_success_url(self):
        messages.success(self.request, _("L'abonnement a été supprimé avec succès"))
        return reverse(
            'userspace:journal:subscription:list', args=(self.current_journal.pk, ))


class IndividualJournalAccessSubscriptionCancelView(
        JournalSubscriptionMixin, SingleObjectTemplateResponseMixin, BaseDetailView):
    force_scope_switch_to_pattern_name = 'userspace:journal:subscription:list'
    model = AccountActionToken
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


class JournalIndividualSubscriptionBatchSubscribe(JournalSubscriptionMixin, TemplateView):
    template_name = 'userspace/journal/subscription/individualsubscription_batch_subscribe.html'

    def parse_csv(self, csv_bytes):
        encoding = chardet.detect(csv_bytes)
        fp = io.StringIO(csv_bytes.decode(encoding['encoding']).strip())
        csvreader = csv.reader(fp, delimiter=';')
        validator = EmailValidator()
        management_subscription = JournalManagementSubscription.objects.get(
            journal=self.current_journal)
        errors = []
        ignored = []
        toadd = []
        for index, row in enumerate(csvreader):
            try:
                (email, first_name, last_name) = row
                validator(email)
                assert ';' not in first_name
                assert ';' not in last_name
            except (ValidationError, AssertionError, ValueError):
                errors.append((index + 1, ';'.join(row)))
            else:
                if management_subscription.email_exists_or_is_pending(email):
                    ignored.append(email)
                else:
                    toadd.append((email, first_name, last_name))
        if errors:
            # When there are errors, we don't show any toadd/ignored
            toadd = []
            ignored = []
        return toadd, ignored, errors

    def post(self, request, *args, **kwargs):
        management_subscription = JournalManagementSubscription.objects.get(
            journal=self.current_journal)
        slots_left = management_subscription.slots_left
        toadd = request.POST.getlist('toadd')
        send_email = request.POST.get('send_email')
        if toadd:
            toadd = toadd[:slots_left]
            for line in toadd:
                email, first_name, last_name = line.split(';')
                if send_email:
                    AccountActionToken.objects.create(
                        email=email,
                        first_name=first_name,
                        last_name=last_name,
                        action=IndividualSubscriptionAction.name,
                        content_object=management_subscription,
                    )

                if not send_email:
                    management_subscription.subscribe_email(
                        email,
                        firstname=first_name,
                        lastname=last_name
                    )

            msg = ngettext(
                "{} invitation d'abonnement a été envoyée avec succès.",
                "{} invitations d'abonnement ont été envoyées avec succès.",
                len(toadd)
            ).format(len(toadd))
            messages.success(request, msg)
            url = reverse(
                'userspace:journal:subscription:list', args=(self.current_journal.pk, ))
            return HttpResponseRedirect(url)
        else:
            contents = request.FILES['csvfile'].read()
            try:
                toadd, ignored, errors = self.parse_csv(contents)
                if slots_left >= len(toadd):
                    kwargs.update({
                        'errors': errors,
                        'ignored': ignored,
                        'toadd': toadd,
                    })
                else:
                    msg = _(
                        "Vous tentez d'abonner {} personnes alors qu'il reste {} places à votre "
                        "forfait."
                    ).format(len(toadd), slots_left)
                    messages.error(request, msg)
            except ValueError:
                messages.error(request, _("Le CSV fourni n'est pas du bon format."))
        return self.get(request, *args, **kwargs)


class JournalIndividualSubscriptionBatchDelete(JournalSubscriptionMixin, TemplateView):
    template_name = 'userspace/journal/subscription/individualsubscription_batch_delete.html'

    def get_queryset(self):
        return JournalAccessSubscription.objects.filter(
            journal_management_subscription__journal=self.current_journal,
        )

    def parse_csv(self, csv_bytes):
        fp = io.StringIO(csv_bytes.decode('utf-8').strip())
        csvreader = csv.reader(fp)
        validator = EmailValidator()
        errors = []
        ignored = []
        todelete = []
        qs = self.get_queryset()
        for index, (email, ) in enumerate(csvreader):
            # Spreadsheet apps exporting one column to CSV sometimes append a delimiter at the
            # end of the line. Ignore it so we can parse the email correctly.
            email = email.rstrip(';')
            try:
                validator(email)
            except ValidationError:
                errors.append((index + 1, email))
            else:
                try:
                    subscription = qs.filter(user__email=email).get()
                    todelete.append(subscription)
                except JournalAccessSubscription.DoesNotExist:
                    ignored.append(email)
        if errors:
            # When there are errors, we don't show any todelete/ignored
            todelete = []
            ignored = []
        return todelete, ignored, errors

    def post(self, request, *args, **kwargs):
        todelete = request.POST.getlist('todelete')
        if todelete:
            qs = self.get_queryset().filter(pk__in=todelete)
            deleted_count = qs.count()
            qs.delete()
            msg = ngettext(
                "{} abonnement a été supprimé avec succès.",
                "{} abonnements ont été supprimé avec succès.",
                deleted_count
            ).format(deleted_count)
            messages.success(request, msg)
            url = reverse(
                'userspace:journal:subscription:list', args=(self.current_journal.pk, ))
            return HttpResponseRedirect(url)
        else:
            contents = request.FILES['csvfile'].read()
            try:
                todelete, ignored, errors = self.parse_csv(contents)
                kwargs.update({
                    'errors': errors,
                    'ignored': ignored,
                    'todelete': todelete,
                })
            except ValueError:
                messages.error(request, _("Le CSV fourni n'est pas du bon format."))
        return self.get(request, *args, **kwargs)


class JournalOrganisationSubscriptionList(JournalSubscriptionMixin, TemplateView):
    permission_required = 'subscription.manage_institutional_subscription'
    template_name = 'userspace/journal/subscription/organisationsubscription_list.html'
    ARCHIVE_SUBPATH = 'Abonnements/Abonnes'
    is_org_view = True

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


class JournalOrganisationSubscriptionExport(JournalSubscriptionMixin, View):
    permission_required = 'subscription.manage_institutional_subscription'
    is_org_view = True

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
    permission_required = 'subscription.manage_institutional_subscription'
    AUTHORIZED_SUBPATH = 'Abonnements/Abonnes'
