# -*- coding: utf-8 -*-

from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http import Http404
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import ListView

from base.viewmixins import LoginRequiredMixin
from base.viewmixins import MenuItemMixin
from core.authorization.defaults import AuthorizationConfig
from core.authorization.models import Authorization
from core.subscription.models import JournalManagementSubscription

from ..viewmixins import JournalScopePermissionRequiredMixin

from .forms import AuthorizationForm


class AuthorizationUserView(
        LoginRequiredMixin, JournalScopePermissionRequiredMixin, MenuItemMixin, ListView):
    menu_journal = 'authorization'
    model = Authorization
    permission_required = 'authorization.manage_authorizations'
    template_name = 'userspace/journal/authorization/authorization_user.html'

    def get_queryset(self):
        qs = super(AuthorizationUserView, self).get_queryset()
        ct = ContentType.objects.get(app_label='erudit', model='journal')
        return qs.filter(content_type=ct, object_id=self.current_journal.pk)

    def get_authorizations_per_app(self):
        data = {}

        for choice in AuthorizationConfig.get_choices():
            data[choice[0]] = {
                'authorizations': self.object_list.filter(authorization_codename=choice[0]),
                'label': choice[1],
            }

        # Special case: the subscription authorizations cannot be granted if the current journal
        # is not associated with a management plan.
        if AuthorizationConfig.can_manage_individual_subscription.codename in data:
            if not JournalManagementSubscription.objects.filter(journal=self.current_journal) \
                    .exists():
                data.pop(AuthorizationConfig.can_manage_individual_subscription.codename)

        return data

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['authorizations'] = self.get_authorizations_per_app()
        return data


class AuthorizationCreateView(
        LoginRequiredMixin, JournalScopePermissionRequiredMixin, MenuItemMixin, CreateView):
    menu_journal = 'authorization'
    model = Authorization
    form_class = AuthorizationForm
    permission_required = 'authorization.manage_authorizations'
    template_name = 'userspace/journal/authorization/authorization_create.html'

    def get_authorization_definition(self):
        """ Returns a tuple of the form (codename, label) for the considered authorization. """
        authorization_labels_dict = dict(AuthorizationConfig.get_choices())
        try:
            codename = self.request.GET.get('codename', None)
            assert codename is not None
            assert codename in authorization_labels_dict
        except AssertionError:
            raise Http404
        return codename, authorization_labels_dict[codename]

    def get_context_data(self, **kwargs):
        context = super(AuthorizationCreateView, self).get_context_data(**kwargs)
        context['authorization_codename'], context['authorization_label'] \
            = self.authorization_definition
        return context

    def get_form_kwargs(self):
        kwargs = super(AuthorizationCreateView, self).get_form_kwargs()
        authorization_def = self.authorization_definition

        kwargs.update({
            'codename': authorization_def[0],
            'journal': self.current_journal,
        })

        return kwargs

    def get_success_url(self):
        messages.success(self.request, _("L'accès a été créé avec succès"))
        return reverse('userspace:journal:authorization:list', args=(self.current_journal.id, ))

    authorization_definition = cached_property(get_authorization_definition)


class AuthorizationDeleteView(
        LoginRequiredMixin, JournalScopePermissionRequiredMixin, MenuItemMixin, DeleteView):
    menu_journal = 'authorization'
    model = Authorization
    permission_required = 'authorization.manage_authorizations'
    template_name = 'userspace/journal/authorization/authorization_confirm_delete.html'

    def get_success_url(self):
        messages.success(self.request, _("L'accès a été supprimé avec succès"))
        return reverse('userspace:journal:authorization:list', args=(self.current_journal.id, ))

    def get_permission_object(self):
        authorization = self.get_object()
        return authorization.content_object
