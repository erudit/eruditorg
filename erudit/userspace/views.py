from django.core.urlresolvers import reverse
from django.views.generic import (TemplateView, CreateView,
                                  DeleteView, ListView)
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType

from rules.contrib.views import PermissionRequiredMixin

from permissions.models import Rule

from .forms import RuleForm


class LoginRequiredMixin(object):

    @classmethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        return login_required(view)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'userspace/dashboard.html'


class PermissionsCheckMixin(PermissionRequiredMixin, LoginRequiredMixin):
    permission_required = 'userspace.manage_permissions'

    def get_queryset(self):
        qs = super(PermissionsCheckMixin, self).get_queryset()
        ct = ContentType.objects.get(app_label="erudit", model="journal")
        ids = [j.id for j in self.request.user.journals.all()]
        return qs.filter(content_type=ct, object_id__in=ids)


class PermissionsListView(PermissionsCheckMixin, ListView):
    model = Rule
    template_name = 'userspace/perm_list.html'


class PermissionsCreateView(PermissionsCheckMixin, CreateView):
    model = Rule
    form_class = RuleForm
    template_name = 'userspace/perm_create.html'

    def get_form_kwargs(self):
        kwargs = super(PermissionsCreateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse('userspace:perm_list')


class PermissionsDeleteView(PermissionsCheckMixin, DeleteView):
    model = Rule
    template_name = 'userspace/perm_confirm_delete.html'

    def get_success_url(self):
        return reverse('userspace:perm_list')

    def get_permission_object(self):
        rule = self.get_object()
        return rule.content_object
