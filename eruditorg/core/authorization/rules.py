# -*- coding: utf-8 -*-

import rules
from rules.predicates import is_staff
from rules.predicates import is_superuser

from core.journal.predicates import is_journal_member

from .defaults import AuthorizationConfig as AC
from .predicates import HasAuthorization


# This permission assume to use a 'Journal' object to perform the perm check
rules.add_perm(
    "authorization.manage_authorizations",
    is_superuser | is_staff | is_journal_member & HasAuthorization(AC.can_manage_authorizations),
)
