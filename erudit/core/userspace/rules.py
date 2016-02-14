from django.contrib.contenttypes.models import ContentType
import rules
from rules.predicates import is_staff, is_superuser
from core.permissions.models import Rule
from core.permissions.predicates import HasPermission


@rules.predicate
def can_manage_permissions(user, journal=None):
    if journal is None:
        return bool(Rule.objects.filter(
            user=user,
            permission='userspace.manage_permissions').count())
    else:
        ct = ContentType.objects.get(app_label="erudit", model="journal")
        return bool(Rule.objects.filter(
            user=user,
            content_type=ct,
            object_id=journal.id,
            permission='userspace.manage_permissions').count())

rules.add_perm('userspace.manage_permissions',
               is_superuser | is_staff |
               HasPermission("userspace.manage_permissions"))
