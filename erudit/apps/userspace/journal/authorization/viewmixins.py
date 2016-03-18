# -*- coding: utf-8 -*-

from django.contrib.contenttypes.models import ContentType
from rules.contrib.views import PermissionRequiredMixin


class PermissionsCheckMixin(PermissionRequiredMixin):
    permission_required = 'authorization.manage_authorizations'

    def get_queryset(self):
        qs = super(PermissionsCheckMixin, self).get_queryset()
        ct = ContentType.objects.get(app_label="erudit", model="journal")
        return qs.filter(content_type=ct, object_id=self.current_journal.pk)

    def get_permission_object(self):
        return self.current_journal
