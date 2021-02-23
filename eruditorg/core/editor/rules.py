# -*- coding: utf-8 -*-

import rules
from rules.predicates import is_authenticated
from rules.predicates import is_staff
from rules.predicates import is_superuser

from core.authorization.defaults import AuthorizationConfig as AC
from core.authorization.predicates import HasAuthorization
from core.journal.predicates import is_journal_member


# This permission assume to use a 'Journal' object to perform the perm check
rules.add_perm(
    "editor.manage_issuesubmission",
    is_authenticated
    & (
        is_superuser
        | is_staff
        | (is_journal_member & HasAuthorization(AC.can_manage_issuesubmission))
    ),
)

rules.add_perm(
    "editor.review_issuesubmission",
    is_authenticated & (is_superuser | HasAuthorization(AC.can_review_issuesubmission)),
)
