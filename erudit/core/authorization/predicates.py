# -*- coding: utf-8 -*-

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
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
            if user.is_anonymous():
                # Anonymous users cannot have authorizations.
                return False

            user_model = get_user_model()
            user_groups_related_name = user_model.groups.field.related_query_name()

            # Defines the main Authorization queryset
            authorization_qs = Authorization.objects \
                .filter(authorization_codename=authorization_codename) \
                .filter(Q(**{'group__{}'.format(user_groups_related_name): user}) | Q(user=user))

            if obj is not None:
                if foreign_key:
                    obj = getattr(obj, foreign_key)
                app_label = obj._meta.app_label
                model_name = obj.__class__.__name__.lower()
                ct = ContentType.objects.get(app_label=app_label, model=model_name)
                authorization_qs = authorization_qs.filter(content_type=ct, object_id=obj.id)

            return authorization_qs.exists()

        return Predicate(check)
