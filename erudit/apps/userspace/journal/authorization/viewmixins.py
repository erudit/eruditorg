from django.contrib.contenttypes.models import ContentType
from rules.contrib.views import PermissionRequiredMixin

from base.viewmixins import LoginRequiredMixin


class PermissionsCheckMixin(PermissionRequiredMixin, LoginRequiredMixin):
    permission_required = 'authorization.manage_authorizations'

    def get_queryset(self):
        qs = super(PermissionsCheckMixin, self).get_queryset()
        ct = ContentType.objects.get(app_label="erudit", model="journal")
        ids = [j.id for j in self.request.user.journals.all()]
        return qs.filter(content_type=ct, object_id__in=ids)
