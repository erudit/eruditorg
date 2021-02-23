# -*- coding: utf-8 -*-

import rules
from rules.predicates import is_authenticated
from rules.predicates import is_staff
from rules.predicates import is_superuser

from .predicates import is_organisation_member


rules.add_perm(
    "library.has_access_to_dashboard",
    is_authenticated & (is_superuser | is_staff | is_organisation_member),
)
