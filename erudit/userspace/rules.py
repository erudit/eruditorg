from django.contrib.contenttypes.models import ContentType

import rules

from permissions.models import Rule


@rules.predicate
def is_superuser(user):
    return user.is_superuser


@rules.predicate
def is_staff(user):
    return user.is_staff


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
               is_superuser | is_staff | can_manage_permissions)
