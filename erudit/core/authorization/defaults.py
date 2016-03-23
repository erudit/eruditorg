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
        'authorization:can_manage_authorizations', _("Autorisations"))
    """
    This authorization defines the ability to add or delete authorizations to specific users.
    """

    can_manage_issuesubmission = AuthorizationDef(
        'editor:can_manage_issuesubmission', _('Dépôt de fichiers'))
    """
    This authorization defines the ability to handle issue submissions.
    """

    can_review_issuesubmission = AuthorizationDef(
        'editor:can_review_issuesubmission', _('Valider les numéros'))
    """
    This authorization defines the ability to review issue submissions.
    """

    can_manage_individual_subscription = AuthorizationDef(
        'subscriptions:can_manage_individual_subscription', _('Valider les numéros'))
    """
    This authorization defines the ability to handle the individual subscriptions to journals.
    """

    @classmethod
    def get_choices(cls):
        vattrs = inspect.getmembers(cls)
        return [(a[1].codename, a[1].label) for a in vattrs if isinstance(a[1], AuthorizationDef)]
