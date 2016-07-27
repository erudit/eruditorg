# -*- coding: utf-8 -*-

import inspect

from django.utils.translation import ugettext_lazy as _


class AuthorizationDef(object):
    def __init__(self, codename, label, staff_only=False):
        self.codename = codename
        self.label = label
        self.staff_only = staff_only


class AuthorizationConfig(object):
    """ Defines the authorizations that can be given to users in the Érudit application. """

    can_manage_authorizations = AuthorizationDef(
        'authorization:can_manage_authorizations', _('Autorisations'))
    """
    This authorization defines the ability to add or delete authorizations to specific users.
    """

    can_edit_journal_information = AuthorizationDef(
        'editor:can_edit_journal_information', _('Éditer les informations de revues'))
    """
    This authorization defines the ability to update journal information.
    """

    can_manage_issuesubmission = AuthorizationDef(
        'editor:can_manage_issuesubmission', _('Dépôt de fichiers'))
    """
    This authorization defines the ability to handle issue submissions.
    """

    can_review_issuesubmission = AuthorizationDef(
        'editor:can_review_issuesubmission', _('Valider les numéros'), staff_only=True)
    """
    This authorization defines the ability to review issue submissions.
    """

    can_manage_individual_subscription = AuthorizationDef(
        'subscriptions:can_manage_individual_subscription', _('Abonnements'))
    """
    This authorization defines the ability to handle the individual subscriptions to journals.
    """

    can_manage_organisation_subscription_ips = AuthorizationDef(
        'subscriptions:can_manage_organisation_subscription_ips',
        _("Gestion des adresses IP de l'abonnement"))
    """
    This authorization defines the ability to handle the IPs of an organisation subscriptions to
    journals.
    """

    can_manage_organisation_subscription_information = AuthorizationDef(
        'subscriptions:can_manage_organisation_subscription_information',
        _("Gestion des informations d'un abonnement"))
    """
    This authorization defines the ability to manage the information of an organisation
    subscription.
    """

    can_manage_organisation_members = AuthorizationDef(
        'subscriptions:can_manage_organisation_members',
        _("Gestion des membres d'un abonnement"))
    """
    This authorization defines the ability to manage the members of an organisation.
    """

    can_consult_royalty_reports = AuthorizationDef(
        'royalty_reports:can_consult_royalty_reports',
        _('Consultation des rapports de redevances'))
    """
    This authorization defines the ability to consult the royalty reports.
    """

    @classmethod
    def get_choices(cls, include_staff_only=False):
        authorizations = []
        for vattr in inspect.getmembers(cls):
            if isinstance(vattr[1], AuthorizationDef) and (
                include_staff_only or not vattr[1].staff_only
            ):
                authorizations.append(
                    (vattr[1].codename, vattr[1].label)
                )
        return authorizations
