# -*- coding: utf-8 -*-

import rules
from rules.predicates import is_authenticated
from rules.predicates import is_staff
from rules.predicates import is_superuser
from core.journal.predicates import can_manage_a_journal
from core.subscription.predicates import can_manage_an_organisation

# This permission assume to use a 'Journal' object to perform the perm check
rules.add_perm(
    "userspace.access",
    is_authenticated
    & (is_superuser | is_staff | can_manage_a_journal | can_manage_an_organisation),
)

rules.add_perm(
    "userspace.staff_access",
    is_authenticated & (is_superuser | is_staff),
)
