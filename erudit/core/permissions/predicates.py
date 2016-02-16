from django.contrib.contenttypes.models import ContentType

from rules import Predicate

from core.permissions.models import Rule


class HasPermission(object):
    """
    Class generator which return a predicate function parametrized by a
    permission name.
    """

    def __new__(cls, permission_name, foreign_key=None):
        def check(user, obj=None):
            if obj is None:
                return bool(Rule.objects.filter(
                    user=user,
                    permission=permission_name).count())
            else:
                if foreign_key:
                    obj = getattr(obj, foreign_key)
                app_label = obj._meta.app_label
                model_name = obj.__class__.__name__.lower()
                ct = ContentType.objects.get(app_label=app_label,
                                             model=model_name)
                return bool(Rule.objects.filter(
                    user=user,
                    content_type=ct,
                    object_id=obj.id,
                    permission=permission_name).count())

        return Predicate(check)
