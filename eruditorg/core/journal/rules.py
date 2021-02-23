# -*- coding: utf-8 -*-

import rules
from rules.predicates import is_authenticated
from rules.predicates import is_staff
from rules.predicates import is_superuser

from core.authorization.defaults import AuthorizationConfig as AC
from core.authorization.predicates import HasAuthorization
from core.subscription.rules import has_valid_subscription

from .predicates import can_edit_journal


rules.add_perm(
    "journal.edit_journal_information",
    is_authenticated
    & (
        is_superuser
        | is_staff
        | (can_edit_journal & HasAuthorization(AC.can_edit_journal_information))
    ),
)

rules.add_perm(
    "journal.manage_organisation_members",
    is_authenticated
    & (
        is_superuser
        | is_staff
        | (has_valid_subscription & HasAuthorization(AC.can_manage_organisation_members))
    ),
)
