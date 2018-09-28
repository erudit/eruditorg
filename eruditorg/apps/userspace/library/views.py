# -*- coding: utf-8 -*-

from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.views.generic import RedirectView
from django.views.generic import TemplateView

from base.viewmixins import LoginRequiredMixin

from .shortcuts import get_managed_organisations
from .viewmixins import OrganisationScopeMixin


class HomeView(LoginRequiredMixin, OrganisationScopeMixin, TemplateView):
    template_name = 'userspace/library/home.html'


class LibrarySectionEntryPointView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        organisations_qs = get_managed_organisations(self.request.user)
        organisations_count = organisations_qs.count()
        if organisations_count:
            return reverse(
                'userspace:library:home', kwargs={
                    'organisation_pk': organisations_qs.first().pk})
        else:
            # No Journal instance can be edited
            raise PermissionDenied
