# -*- coding: utf-8 -*-

from django import template

from core.authorization.defaults import AuthorizationConfig as AC
from core.authorization.models import Authorization
from erudit.models import Journal

register = template.Library()


@register.filter
def can_access_userspace(user):
    """ Returns a boolean indicating if the user can access the userspace. """
    return user.is_superuser or user.is_staff or (
        user.is_authenticated() and
        Journal.objects.filter(members=user).exists() and
        Authorization.objects.filter(
            user=user,
            authorization_codename__in=[
                AC.can_manage_authorizations.codename,
                AC.can_manage_issuesubmission.codename,
                AC.can_manage_individual_subscription.codename,
            ]
        ).exists()
    )
