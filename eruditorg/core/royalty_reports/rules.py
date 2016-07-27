# -*- coding: utf-8 -*-

import rules
from rules.predicates import is_authenticated
from rules.predicates import is_staff
from rules.predicates import is_superuser

from core.authorization.defaults import AuthorizationConfig as AC
from core.authorization.predicates import HasAuthorization


rules.add_perm(
    'royalty_reports.consult_royalty_reports',
    is_authenticated & (
        is_superuser | is_staff | HasAuthorization(AC.can_consult_royalty_reports)
    ),
)
