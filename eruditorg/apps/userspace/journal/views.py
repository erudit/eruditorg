# -*- coding: utf-8 -*-

from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.views.generic import RedirectView
from django.views.generic import TemplateView

from base.viewmixins import LoginRequiredMixin
from core.journal.rules_helpers import get_editable_journals

from .viewmixins import JournalScopeMixin


class HomeView(LoginRequiredMixin, JournalScopeMixin, TemplateView):
    template_name = 'userspace/journal/home.html'


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
