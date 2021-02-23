# -*- coding: utf-8 -*-

from account_actions.models import AccountActionToken
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import ListView
from django.views.generic.detail import BaseDetailView
from django.views.generic.detail import SingleObjectTemplateResponseMixin

from django.contrib.auth.mixins import LoginRequiredMixin
from base.viewmixins import MenuItemMixin

from ..viewmixins import OrganisationScopePermissionRequiredMixin

from .forms import OrganisationMembershipTokenCreateForm


class OrganisationMemberListView(
    LoginRequiredMixin, OrganisationScopePermissionRequiredMixin, MenuItemMixin, ListView
):
    context_object_name = "members"
    menu_library = "members"
    paginate_by = 10
    permission_required = "userspace.staff_access"
    template_name = "userspace/library/members/member_list.html"

    def get_context_data(self, **kwargs):
        context = super(OrganisationMemberListView, self).get_context_data(**kwargs)
        context["pending_members"] = AccountActionToken.pending_objects.get_for_object(
            self.current_organisation
        )
        return context

    def get_queryset(self):
        return self.current_organisation.members.order_by("pk")


class OrganisationMemberCreateView(
    LoginRequiredMixin, OrganisationScopePermissionRequiredMixin, MenuItemMixin, CreateView
):
    form_class = OrganisationMembershipTokenCreateForm
    menu_library = "members"
    model = AccountActionToken
    permission_required = "userspace.staff_access"
    template_name = "userspace/library/members/member_create.html"

    def get_form_kwargs(self):
        kwargs = super(OrganisationMemberCreateView, self).get_form_kwargs()
        kwargs.update({"organisation": self.current_organisation})
        return kwargs

    def get_success_url(self):
        messages.success(self.request, _("Le membre a été invité avec succès."))
        return reverse("userspace:library:members:list", args=(self.current_organisation.pk,))


class OrganisationMemberDeleteView(
    LoginRequiredMixin, OrganisationScopePermissionRequiredMixin, MenuItemMixin, DeleteView
):
    context_object_name = "member"
    force_scope_switch_to_pattern_name = "userspace:library:members:list"
    menu_library = "members"
    permission_required = "userspace.staff_access"
    template_name = "userspace/library/members/member_delete.html"

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.current_organisation.members.remove(self.object)
        success_url = self.get_success_url()
        return HttpResponseRedirect(success_url)

    def get_queryset(self):
        return self.current_organisation.members.all()

    def get_success_url(self):
        messages.success(self.request, _("Le membre a été retiré de l’organisation avec succès."))
        return reverse("userspace:library:members:list", args=(self.current_organisation.pk,))


class OrganisationMemberCancelView(
    LoginRequiredMixin,
    OrganisationScopePermissionRequiredMixin,
    MenuItemMixin,
    SingleObjectTemplateResponseMixin,
    BaseDetailView,
):
    force_scope_switch_to_pattern_name = "userspace:library:members:list"
    menu_library = "members"
    model = AccountActionToken
    permission_required = "userspace.staff_access"
    template_name = "userspace/library/members/member_cancel.html"

    def get_queryset(self):
        return AccountActionToken.pending_objects.filter(
            content_type=ContentType.objects.get_for_model(self.current_organisation),
            object_id=self.current_organisation.id,
        )

    def post(self, request, *args, **kwargs):
        self.request = request
        self.object = self.get_object()
        self.object.cancel()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        messages.success(self.request, _("La proposition a été annulée avec succès."))
        return reverse("userspace:library:members:list", args=(self.current_organisation.pk,))
