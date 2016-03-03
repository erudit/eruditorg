from django.core.urlresolvers import reverse
from django.views.generic import (TemplateView, CreateView,
                                  DeleteView, ListView)
from django.utils.translation import ugettext_lazy as _

from core.permissions.models import ObjectPermission
from apps.userspace.viewmixins import (LoginRequiredMixin,
                                       UserspaceBreadcrumbsMixin)
from apps.userspace.permissions.viewmixins import (PermissionsCheckMixin,
                                                   PermissionsBreadcrumbsMixin)
from .forms import ObjectPermissionForm


class DashboardView(UserspaceBreadcrumbsMixin, LoginRequiredMixin, TemplateView):
    template_name = 'userspace/dashboard.html'


class PermissionsListView(PermissionsBreadcrumbsMixin,
                          PermissionsCheckMixin, ListView):
    model = ObjectPermission
    template_name = 'userspace/permissions/perm_list.html'


class PermissionsCreateView(PermissionsBreadcrumbsMixin,
                            PermissionsCheckMixin, CreateView):
    model = ObjectPermission
    form_class = ObjectPermissionForm
    template_name = 'userspace/permissions/perm_create.html'
    title = _("Ajouter une permission")

    def get_form_kwargs(self):
        kwargs = super(PermissionsCreateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse('userspace:permissions:perm_list')


class PermissionsDeleteView(PermissionsBreadcrumbsMixin,
                            PermissionsCheckMixin, DeleteView):
    model = ObjectPermission
    template_name = 'userspace/permissions/perm_confirm_delete.html'

    def get_title(self):
        return _("Supprimer une permission")

    def get_success_url(self):
        return reverse('userspace:permissions:perm_list')

    def get_permission_object(self):
        rule = self.get_object()
        return rule.content_object
