# -*- coding: utf-8 -*-

import inspect

from django.utils.translation import ugettext_lazy as _


class AuthorizationDef(object):
    def __init__(self, codename, label):
        self.codename = codename
        self.label = label


class AuthorizationConfig(object):
    """ Defines the authorizations that can be given to users in the Érudit application. """

    can_manage_authorizations = AuthorizationDef(
        'authorization:can_manage_authorizations', _("Peut gérer les autorisation"))
    """
    This authorization defines the ability to add or delete authorizations to specific users.
    """

    can_manage_account = AuthorizationDef(
        'subscriptions:can_manage_account', _("Peut gérer les abonnements individuels"))
    """
    This authorization defines the ability to handle the subscriptions of the account.
    """

    can_manage_issuesubmission = AuthorizationDef(
        'subscriptions:can_manage_issuesubmission', _('Peut gérer les numéros'))
    """
    This authorization defines the ability to handle issue submissions.
    """

    can_review_issuesubmission = AuthorizationDef(
        'subscriptions:can_review_issuesubmission', _('Peut valider les numéros'))
    """
    This authorization defines the ability to review issue submissions.
    """

    @classmethod
    def get_choices(cls):
        vattrs = inspect.getmembers(cls)
        return [(a[1].codename, a[1].label) for a in vattrs if isinstance(a[1], AuthorizationDef)]
