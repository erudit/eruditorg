# -*- coding: utf-8 -*-

from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from rules.contrib.views import PermissionRequiredMixin

from base.viewmixins import LoginRequiredMixin
from core.journal.rules_helpers import get_editable_journals
from erudit.models import Journal


class JournalScopeMixin:
    """
    The JournalScopeMixin provides a way to associate a view with a specific Journal instance. The
    Journal instance must have the current user in its members. If not a PermissionDenied error will
    be returned.
    """
    force_scope_switch_to_pattern_name = None
    scope_session_key = 'userspace:journal-management:current-journal-id'

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        response = self.init_scope()
        return response if response \
            else super(JournalScopeMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(JournalScopeMixin, self).get_context_data(**kwargs)
        context['scope_current_journal'] = self.current_journal
        context['scope_user_journals'] = self.user_journals
        context['force_scope_switch_to_pattern_name'] = self.force_scope_switch_to_pattern_name
        return context

    def get_user_journals(self):
        """ Returns the journals that can be accessed by the current user. """
        return get_editable_journals(self.request.user)

    def init_current_journal(self, journal):
        """ Associates the current journal to the view and saves its ID into the session. """
        self.current_journal = journal
        self.request.session[self.scope_session_key] = journal.id

    def init_scope(self):
        """ Initializes the Journal scope. """
        scoped_url = self.kwargs.get('journal_pk') is not None

        # We try to determine the current Journal instance by looking
        # first in the URL. If the journal ID cannot be retrieved from there
        # we try to fetch it from the session.
        current_journal_id = self.kwargs.get('journal_pk', None) \
            or self.request.session.get(self.scope_session_key, None)

        journal = None

        if current_journal_id is not None:
            journal = get_object_or_404(Journal, id=current_journal_id)
        else:
            user_journals_qs = self.user_journals
            user_journal_count = user_journals_qs.count()
            if user_journal_count:
                journal = user_journals_qs.first()

        # Returns a 403 error if the user is not a member of the journal
        if journal is None or not self.user_journals.filter(id=journal.id).exists():
            raise PermissionDenied

        if not scoped_url:
            # Redirects to the scoped URL
            resolver_match = self.request.resolver_match
            args = resolver_match.args
            kwargs = resolver_match.kwargs.copy()
            kwargs.update({'journal_pk': journal.pk})
            url = reverse(
                ':'.join([resolver_match.namespace, resolver_match.url_name]),
                args=args, kwargs=kwargs)
            if self.request.GET:
                url = '{}?{}'.format(url, self.request.GET.urlencode())
            return HttpResponseRedirect(url)

        self.init_current_journal(journal)

    @cached_property
    def user_journals(self):
        return self.get_user_journals()


class JournalScopePermissionRequiredMixin(
        LoginRequiredMixin, JournalScopeMixin, PermissionRequiredMixin):
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super(JournalScopePermissionRequiredMixin, self).get_context_data(**kwargs)
        context['journal_permission_required'] = self.permission_required
        return context

    def get_permission_object(self):
        return self.current_journal
