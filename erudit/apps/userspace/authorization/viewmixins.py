from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from rules.contrib.views import PermissionRequiredMixin
from navutils import Breadcrumb

from apps.userspace.viewmixins import (LoginRequiredMixin,
                                       UserspaceBreadcrumbsMixin)


class PermissionsCheckMixin(PermissionRequiredMixin, LoginRequiredMixin):
    permission_required = 'authorization.manage_authorizations'

    def get_queryset(self):
        qs = super(PermissionsCheckMixin, self).get_queryset()
        ct = ContentType.objects.get(app_label="erudit", model="journal")
        ids = [j.id for j in self.request.user.journals.all()]
        return qs.filter(content_type=ct, object_id__in=ids)


class PermissionsBreadcrumbsMixin(UserspaceBreadcrumbsMixin):

    def get_breadcrumbs(self):
        breadcrumbs = super(PermissionsBreadcrumbsMixin, self).get_breadcrumbs()
        breadcrumbs.append(Breadcrumb(
            _("Permissions"),
            pattern_name='userspace:authorization:authorization_list'))
        return breadcrumbs
