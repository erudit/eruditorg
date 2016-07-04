# -*- coding: utf-8 -*-

from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.views.generic import RedirectView
from django.views.generic import TemplateView
from erudit.models import Journal

from base.viewmixins import LoginRequiredMixin
from core.editor.shortcuts import is_production_team_member
from core.journal.rules_helpers import get_editable_journals

from .viewmixins import JournalScopeMixin


class HomeView(LoginRequiredMixin, JournalScopeMixin, TemplateView):
    allow_production_team_access = True
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
        journal_qs = Journal.objects.filter(collection__code='erudit') \
            if is_production_team_member(self.request.user) \
            else get_editable_journals(self.request.user)
        journal_count = journal_qs.count()
        if journal_count:
            return reverse(
                'userspace:journal:home', kwargs={
                    'journal_pk': journal_qs.first().pk})
        else:
            # No Journal instance can be edited
            raise PermissionDenied
