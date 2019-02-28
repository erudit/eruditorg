from datetime import datetime

from ipware.ip import get_ip
from django.views.generic import TemplateView

from django.contrib.auth.mixins import LoginRequiredMixin
from base.viewmixins import MenuItemMixin

from core.subscription.models import JournalAccessSubscription
from erudit.models import LegacyOrganisationProfile

from ..viewmixins import OrganisationScopePermissionRequiredMixin


class DiagnosisLandingView(
        LoginRequiredMixin, MenuItemMixin, OrganisationScopePermissionRequiredMixin, TemplateView):
    menu_library = 'diagnosis'
    permission_required = 'library.has_access_to_dashboard'
    template_name = 'userspace/library/diagnosis/landing.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            subscription = JournalAccessSubscription.valid_objects.institutional().get(
                organisation=self.current_organisation
            )
            context['journals'] = subscription.journals.all()
        except JournalAccessSubscription.DoesNotExist:
            context['journals'] = tuple()

        context['date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        context['client_ip'] = get_ip(self.request)
        context['redirection_ip'] = self.request.META.get('REMOTE_ADDR')
        context['user_agent'] = self.request.META.get('HTTP_USER_AGENT')
        try:
            context['identifier'] = self.current_organisation.legacyorganisationprofile.account_id
        except LegacyOrganisationProfile.DoesNotExist:
            context['identifier'] = ''
        context['institution'] = self.current_organisation.name
        return context
