from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView

from base.viewmixins import LoginRequiredMixin
from core.journal.rules_helpers import get_editable_journals
from core.journal.rules_helpers import get_editable_organisations


class UserspaceHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'userspace/home.html'

    def get(self, request):
        journal_qs = get_editable_journals(self.request.user)
        organisation_qs = get_editable_organisations(self.request.user)
        journal_exists = journal_qs.exists()
        organisation_exists = organisation_qs.exists()

        if journal_exists and organisation_exists:
            return self.render_to_response(
                self.get_context_data(journals=journal_qs, organisations=organisation_qs))
        elif journal_exists:
            return HttpResponseRedirect(reverse('userspace:journal:entrypoint'))
        elif organisation_exists:
            return HttpResponseRedirect(reverse('userspace:library:entrypoint'))
        else:
            return HttpResponseRedirect(reverse('public:auth:personal_data'))
