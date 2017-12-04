from datetime import datetime

from django.views.generic import TemplateView

from base.viewmixins import LoginRequiredMixin
from base.viewmixins import MenuItemMixin

from core.subscription.models import JournalAccessSubscription

from ..viewmixins import OrganisationScopePermissionRequiredMixin


class DiagnosisLandingView(
        LoginRequiredMixin, MenuItemMixin, OrganisationScopePermissionRequiredMixin, TemplateView):
    menu_library = 'diagnosis'
    permission_required = 'library.has_access_to_dashboard'
    template_name = 'userspace/library/diagnostic/landing.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            subscription = JournalAccessSubscription.valid_objects.get(
                organisation=self.current_organisation
            )
            context['journals'] = subscription.journals.all()
        except JournalAccessSubscription.DoesNotExist:
            context['journals'] = tuple()

        context['date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        context['client_ip'] = self.request.META.get('HTTP_CLIENT_IP')
        context['redirection_ip'] = self.request.META.get('REMOTE_ADDR')
        context['user_agent'] = self.request.META.get('HTTP_USER_AGENT')
        context['identifier'] = self.current_organisation.legacyorganisationprofile.account_id
        context['institution'] = self.current_organisation.name
        return context
