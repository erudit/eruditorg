# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import ListView

from base.viewmixins import MenuItemMixin
from core.authorization.defaults import AuthorizationConfig
from core.authorization.models import Authorization

from ..viewmixins import JournalScopeMixin

from .forms import AuthorizationForm
from .viewmixins import PermissionsCheckMixin


class AuthorizationUserView(JournalScopeMixin, MenuItemMixin, PermissionsCheckMixin, ListView):
    menu_journal = 'authorization'
    model = Authorization
    template_name = 'userspace/journal/authorization/authorization_user.html'

    def get_authorizations_per_app(self):
        data = {}
        for choice in AuthorizationConfig.get_choices():
            data[choice] = self.object_list.filter(authorization_codename=choice[0])
        return data

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['authorizations'] = self.get_authorizations_per_app()
        return data


class AuthorizationCreateView(JournalScopeMixin, MenuItemMixin, PermissionsCheckMixin, CreateView):
    menu_journal = 'authorization'
    model = Authorization
    form_class = AuthorizationForm
    template_name = 'userspace/journal/authorization/authorization_create.html'
    title = _('Ajouter une autorisation')

    def get_form_kwargs(self):
        kwargs = super(AuthorizationCreateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['codename'] = self.request.GET.get('codename')
        return kwargs

    def get_success_url(self):
        return reverse('userspace:journal:authorization:list', args=(self.current_journal.id, ))


class AuthorizationDeleteView(JournalScopeMixin, MenuItemMixin, PermissionsCheckMixin, DeleteView):
    menu_journal = 'authorization'
    model = Authorization
    template_name = 'userspace/journal/authorization/authorization_confirm_delete.html'
    title = _('Supprimer une autorisation')

    def get_success_url(self):
        return reverse('userspace:journal:authorization:list', args=(self.current_journal.id, ))

    def get_permission_object(self):
        authorization = self.get_object()
        return authorization.content_object
