# -*- coding: utf-8 -*-

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
