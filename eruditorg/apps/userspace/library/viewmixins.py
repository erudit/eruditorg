# -*- coding: utf-8 -*-

from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from rules.contrib.views import PermissionRequiredMixin

from erudit.models import Organisation
from core.subscription.models import JournalAccessSubscription

from .shortcuts import (
    get_managed_organisations,
    get_last_valid_subscription,
    get_last_year_of_subscription,
)


class OrganisationScopeMixin:
    """
    The OrganisationScopeMixin provides a way to associate a view with a specific Organisation
    instance. The Organisation instance must have the current user in its members. If not a
    PermissionDenied error will be returned.
    """

    force_scope_switch_to_pattern_name = None
    scope_session_key = "userspace:library-management:current-organisation-id"

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        response = self.init_scope()
        return (
            response
            if response
            else super(OrganisationScopeMixin, self).dispatch(request, *args, **kwargs)
        )

    def get_context_data(self, **kwargs):
        context = super(OrganisationScopeMixin, self).get_context_data(**kwargs)
        context["scope_current_organisation"] = self.current_organisation
        context["has_active_subscription"] = (
            JournalAccessSubscription.valid_objects.institutional()
            .filter(organisation=self.current_organisation)
            .exists()
        )

        context["last_valid_subscription"] = get_last_valid_subscription(self.current_organisation)
        context["last_year_of_subscription"] = get_last_year_of_subscription(
            self.current_organisation
        )
        context["scope_user_organisations"] = self.user_organisations
        context["force_scope_switch_to_pattern_name"] = self.force_scope_switch_to_pattern_name
        return context

    def get_user_organisations(self):
        """ Returns the organisations that can be accessed by the current user. """
        return get_managed_organisations(self.request.user)

    def init_current_organisation(self, organisation):
        """ Associates the current organisation to the view and saves its ID into the session. """
        self.current_organisation = organisation
        self.request.session[self.scope_session_key] = organisation.id

    def init_scope(self):
        """ Initializes the Organisation scope. """
        scoped_url = self.kwargs.get("organisation_pk") is not None

        # We try to determine the current Organisation instance by looking
        # first in the URL. If the organisation ID cannot be retrieved from there
        # we try to fetch it from the session.
        current_organisation_id = self.kwargs.get(
            "organisation_pk", None
        ) or self.request.session.get(self.scope_session_key, None)

        organisation = None

        if current_organisation_id is not None:
            organisation = get_object_or_404(Organisation, id=current_organisation_id)
        else:
            user_organisations_qs = self.user_organisations
            user_organisations_count = user_organisations_qs.count()
            if user_organisations_count:
                organisation = user_organisations_qs.first()

        # Returns a 403 error if the user is not a member of the organisation

        if organisation is None or not self.user_organisations.filter(id=organisation.id).exists():
            raise PermissionDenied

        if not scoped_url:
            # Redirects to the scoped URL
            resolver_match = self.request.resolver_match
            args = resolver_match.args
            kwargs = resolver_match.kwargs.copy()
            kwargs.update({"organisation_pk": organisation.pk})
            return HttpResponseRedirect(
                reverse(
                    ":".join([resolver_match.namespace, resolver_match.url_name]),
                    args=args,
                    kwargs=kwargs,
                )
            )

        self.init_current_organisation(organisation)

    @cached_property
    def user_organisations(self):
        return self.get_user_organisations()


class OrganisationScopePermissionRequiredMixin(OrganisationScopeMixin, PermissionRequiredMixin):
    raise_exception = True

    def get_context_data(self, **kwargs):

        context = super(OrganisationScopePermissionRequiredMixin, self).get_context_data(**kwargs)
        context["library_permission_required"] = self.permission_required
        return context

    def get_permission_object(self):
        return self.current_organisation
