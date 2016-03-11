# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import ListView

from core.authorization.models import Authorization
from core.authorization.defaults import AuthorizationConfig

from .forms import AuthorizationForm
from .viewmixins import PermissionsCheckMixin
from .viewmixins import PermissionsBreadcrumbsMixin


class AuthorizationUserView(PermissionsBreadcrumbsMixin, PermissionsCheckMixin, ListView):
    model = Authorization
    template_name = 'userspace/authorization/authorization_user.html'

    def get_authorizations_per_app(self):
        data = {}
        for choice in AuthorizationConfig.get_choices():
            data[choice] = self.object_list.filter(authorization_codename=choice[0])
        return data

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['authorizations'] = self.get_authorizations_per_app()
        return data


class AuthorizationListView(PermissionsBreadcrumbsMixin, PermissionsCheckMixin, ListView):
    model = Authorization
    template_name = 'userspace/authorization/authorization_list.html'


class AuthorizationCreateView(PermissionsBreadcrumbsMixin, PermissionsCheckMixin, CreateView):
    model = Authorization
    form_class = AuthorizationForm
    template_name = 'userspace/authorization/authorization_create.html'
    title = _("Ajouter une autorisation")

    def get_form_kwargs(self):
        kwargs = super(AuthorizationCreateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['codename'] = self.request.GET.get('codename')
        return kwargs

    def get_success_url(self):
        return reverse('userspace:authorization:authorization_list')


class AuthorizationDeleteView(PermissionsBreadcrumbsMixin, PermissionsCheckMixin, DeleteView):
    model = Authorization
    template_name = 'userspace/authorization/authorization_confirm_delete.html'

    def get_title(self):
        return _("Supprimer une autorisation")

    def get_success_url(self):
        return reverse('userspace:authorization:authorization_list')

    def get_permission_object(self):
        authorization = self.get_object()
        return authorization.content_object
