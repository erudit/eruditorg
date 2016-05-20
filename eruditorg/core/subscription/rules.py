# -*- coding: utf-8 -*-

import datetime as dt

import rules
from rules.predicates import is_authenticated
from rules.predicates import is_staff
from rules.predicates import is_superuser

from core.authorization.defaults import AuthorizationConfig as AC
from core.authorization.predicates import HasAuthorization
from erudit.rules import is_journal_member

from .models import JournalManagementSubscription


@rules.predicate
def has_journal_management_subscription(user, journal):
    return JournalManagementSubscription.objects.filter(journal=journal).exists()


@rules.predicate
def has_valid_subscription(user, organisation):
    nowd = dt.datetime.now().date()
    return user.organisations.filter(id=organisation.id).exists() and \
        organisation.journalaccesssubscription_set.filter(
            journalaccesssubscriptionperiod__start__lte=nowd,
            journalaccesssubscriptionperiod__end__gte=nowd,
        ).exists()


rules.add_perm(
    'subscription.manage_individual_subscription',
    is_authenticated & (
        is_superuser | is_staff | (
            is_journal_member &
            has_journal_management_subscription &
            HasAuthorization(AC.can_manage_individual_subscription)
        )
    ),
)


rules.add_perm(
    'subscription.manage_organisation_subscription_ips',
    is_authenticated & (
        is_superuser | is_staff | (
            has_valid_subscription &
            HasAuthorization(AC.can_manage_organisation_subscription_ips)
        )
    ),
)
