# -*- coding: utf-8 -*-

import rules
from rules.predicates import is_authenticated
from rules.predicates import is_staff
from rules.predicates import is_superuser

from core.subscription.rules import has_valid_subscription


# This permission assume to use a 'Journal' object to perform the perm check
rules.add_perm(
    'userspace.access_library_stats',
    is_authenticated & (
        is_superuser | is_staff | has_valid_subscription
    ),
)
