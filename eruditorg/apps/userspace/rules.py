# -*- coding: utf-8 -*-

import rules
from rules.predicates import is_authenticated
from rules.predicates import is_staff
from rules.predicates import is_superuser

from core.authorization.defaults import AuthorizationConfig as AC
from core.authorization.predicates import HasAnyAuthorization
from core.journal.predicates import is_journal_member


# This permission assume to use a 'Journal' object to perform the perm check
rules.add_perm(
    'userspace.access',
    is_authenticated & (
        is_superuser | is_staff |
        (
            is_journal_member &
            HasAnyAuthorization([
                AC.can_edit_journal_information,
                AC.can_manage_authorizations,
                AC.can_manage_issuesubmission,
                AC.can_manage_individual_subscription,
            ])
        )
    ),
)
