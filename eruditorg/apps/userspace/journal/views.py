import mimetypes
import os

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.http import HttpResponse, Http404
from django.views.generic import RedirectView, TemplateView, View

from base.viewmixins import LoginRequiredMixin, MenuItemMixin
from core.journal.rules_helpers import get_editable_journals

from .viewmixins import JournalScopeMixin, JournalScopePermissionRequiredMixin


class HomeView(LoginRequiredMixin, JournalScopeMixin, TemplateView):
    template_name = 'userspace/journal/home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)

        # Fetches the JournalInformation instance associated to the current journal
        try:
            journal_info = self.current_journal.information
        except ObjectDoesNotExist:  # pragma: no cover
            pass
        else:
            context['journal_info'] = journal_info

        return context


class JournalSectionEntryPointView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        journal_qs = get_editable_journals(self.request.user)
        journal_count = journal_qs.count()
        if journal_count:
            return reverse(
                'userspace:journal:home', kwargs={
                    'journal_pk': journal_qs.first().pk})
        else:
            # No Journal instance can be edited
            raise PermissionDenied


# Reports

def journal_reports_path(journal_code):
    # The subdirectory in which we place subscription reports is *mostly* the same as journal.code.
    # For some codes, it's been changed.
    if journal_code == 'cd':
        # Cap Aux Diamants
        journal_code = 'cad'
    elif journal_code == 'cd1':
        # Cahiers de Droit
        journal_code = 'cd'
    return os.path.join(settings.SUBSCRIPTION_EXPORTS_ROOT, journal_code)


class BaseReportsDownload(JournalScopePermissionRequiredMixin, View):
    AUTHORIZED_SUBPATH = ''

    def get(self, request, *args, **kwargs):
        subpath = request.GET.get('subpath')
        if not subpath:
            raise Http404()
        fname = os.path.basename(subpath)
        _, ext = os.path.splitext(fname)
        content_type = mimetypes.guess_type(fname)[0]
        response = HttpResponse(content_type=content_type)
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(fname)
        root_path = journal_reports_path(self.current_journal.code)
        path = os.path.normpath(os.path.join(root_path, subpath))
        # Twart attempts to access upper filesystem files. Error out so it shows in sentry.
        assert path.startswith(os.path.join(root_path, self.AUTHORIZED_SUBPATH))
        if not os.path.exists(path):
            raise Http404()
        with open(path, 'rb') as fp:
            response.write(fp.read())
        return response


class RoyaltyReportsDownload(BaseReportsDownload):
    permission_required = 'subscription.consult_royalty_reports'
    AUTHORIZED_SUBPATH = 'Abonnements/Rapports'


class RoyaltiesListView(
        JournalScopePermissionRequiredMixin, MenuItemMixin, TemplateView):
    menu_journal = 'royalty_reports'
    template_name = 'userspace/journal/royalties_list.html'
    permission_required = 'subscription.consult_royalty_reports'
    REPORT_SUBPATH = 'Abonnements/Rapports'

    def get_royalties_reports(self):
        root_path = journal_reports_path(self.current_journal.code)
        result = []
        try:
            toppath = os.path.join(root_path, self.REPORT_SUBPATH)
            for root, dirs, files in os.walk(toppath):
                for fn in files:
                    label = root[len(toppath) + 1:].replace('/', ' - ')
                    result.append((label, root, fn))
            result.sort(reverse=True)
        except FileNotFoundError:
            pass
        return result
