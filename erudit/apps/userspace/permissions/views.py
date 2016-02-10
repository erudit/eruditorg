from django.core.urlresolvers import reverse
from django.views.generic import (TemplateView, CreateView,
                                  DeleteView, ListView)
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView
)
from rules.contrib.views import PermissionRequiredMixin
from navutils import BreadcrumbsMixin, Breadcrumb

from core.permissions.models import Rule
from core.userspace.viewmixins import LoginRequiredMixin

from .forms import RuleForm


class UserspaceBreadcrumbsMixin(BreadcrumbsMixin):
    def get_breadcrumbs(self):
        breadcrumbs = super(UserspaceBreadcrumbsMixin, self).get_breadcrumbs()
        breadcrumbs.append(Breadcrumb(_("Mon espace"),
                                      pattern_name='userspace:dashboard'))
        return breadcrumbs


class LoginRequiredMixin(object):

    @classmethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        return login_required(view)


class DashboardView(UserspaceBreadcrumbsMixin, LoginRequiredMixin, TemplateView):
    template_name = 'userspace/dashboard.html'


>>>>>>>  plug navutils to handle menu and breadcrumb:erudit/userspace/views.py
class PermissionsCheckMixin(PermissionRequiredMixin, LoginRequiredMixin):
    permission_required = 'userspace.manage_permissions'

    def get_queryset(self):
        qs = super(PermissionsCheckMixin, self).get_queryset()
        ct = ContentType.objects.get(app_label="erudit", model="journal")
        ids = [j.id for j in self.request.user.journals.all()]
        return qs.filter(content_type=ct, object_id__in=ids)


class PermissionsBreadcrumbsMixin(UserspaceBreadcrumbsMixin):

    def get_breadcrumbs(self):
        breadcrumbs = super(PermissionsBreadcrumbsMixin, self).get_breadcrumbs()
        breadcrumbs.append(Breadcrumb(_("Permissions"),
                                      pattern_name='userspace:perm_list'))
        return breadcrumbs


class PermissionsListView(PermissionsBreadcrumbsMixin,
                          PermissionsCheckMixin, ListView):
    model = Rule
    template_name = 'userspace/permissions/perm_list.html'


class PermissionsCreateView(PermissionsBreadcrumbsMixin,
                            PermissionsCheckMixin, CreateView):
    model = Rule
    form_class = RuleForm
    template_name = 'userspace/permissions/perm_create.html'
    title = _("Ajouter une permission")

    def get_form_kwargs(self):
        kwargs = super(PermissionsCreateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse('userspace:perm_list')


class PermissionsDeleteView(PermissionsBreadcrumbsMixin,
                            PermissionsCheckMixin, DeleteView):
    model = Rule
    template_name = 'userspace/permissions/perm_confirm_delete.html'

    def get_title(self):
        return _("Supprimer une permission")

    def get_success_url(self):
        return reverse('userspace:perm_list')

    def get_permission_object(self):
        rule = self.get_object()
        return rule.content_object
