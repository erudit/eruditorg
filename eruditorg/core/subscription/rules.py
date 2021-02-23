# -*- coding: utf-8 -*-

import rules
from rules.predicates import is_authenticated
from rules.predicates import is_staff
from rules.predicates import is_superuser

from core.authorization.defaults import AuthorizationConfig as AC
from core.authorization.predicates import HasAuthorization
from core.journal.predicates import is_journal_member

from .models import JournalAccessSubscription
from .models import JournalManagementSubscription


@rules.predicate
def has_journal_management_subscription(user, journal):
    return JournalManagementSubscription.objects.filter(journal=journal).exists()


@rules.predicate
def has_valid_subscription(user, organisation):
    return (
        user.organisations.filter(id=organisation.id).exists()
        and JournalAccessSubscription.valid_objects.institutional()
        .filter(organisation_id=organisation.id)
        .exists()
    )


rules.add_perm(
    "subscription.manage_individual_subscription",
    is_authenticated
    & (
        is_superuser
        | is_staff
        | (
            is_journal_member
            & has_journal_management_subscription
            & HasAuthorization(AC.can_manage_individual_subscription)
        )
    ),
)

rules.add_perm(
    "subscription.manage_institutional_subscription",
    is_authenticated
    & (is_superuser | is_staff | HasAuthorization(AC.can_manage_institutional_subscription)),
)


rules.add_perm(
    "subscription.manage_organisation_subscription_ips",
    is_authenticated
    & (
        is_superuser
        | is_staff
        | (has_valid_subscription & HasAuthorization(AC.can_manage_organisation_subscription_ips))
    ),
)

rules.add_perm(
    "subscription.manage_organisation_subscription_information",
    is_authenticated
    & (
        is_superuser
        | is_staff
        | (
            has_valid_subscription
            & HasAuthorization(AC.can_manage_organisation_subscription_information)
        )
    ),
)

rules.add_perm(
    "subscription.consult_royalty_reports",
    is_authenticated & (is_superuser | is_staff | HasAuthorization(AC.can_consult_royalty_reports)),
)
