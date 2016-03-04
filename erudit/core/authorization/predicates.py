# -*- coding: utf-8 -*-

from django.contrib.contenttypes.models import ContentType
from rules import Predicate

from .defaults import AuthorizationDef
from .models import Authorization


class HasAuthorization(object):
    """
    Class generator which return a predicate function parametrized by an
    authorization codename.
    """

    def __new__(cls, authorization, foreign_key=None):
        authorization_codename = authorization.codename \
            if isinstance(authorization, AuthorizationDef) else authorization

        def check(user, obj=None):
            if obj is None:
                return bool(Authorization.objects.filter(
                    user=user, authorization_codename=authorization_codename).count())
            else:
                if foreign_key:
                    obj = getattr(obj, foreign_key)
                app_label = obj._meta.app_label
                model_name = obj.__class__.__name__.lower()
                ct = ContentType.objects.get(app_label=app_label, model=model_name)
                return bool(Authorization.objects.filter(
                    user=user, content_type=ct, object_id=obj.id,
                    authorization_codename=authorization_codename).count())

        return Predicate(check)
