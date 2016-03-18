# -*- coding: utf-8 -*-

import rules
from rules.predicates import is_authenticated
from rules.predicates import is_staff
from rules.predicates import is_superuser

from .models import Policy


@rules.predicate
def is_policy_manager(user, policy=None):
    if policy is None:
        return bool(Policy.objects.filter(managers=user).count())
    else:
        return bool(policy.managers.filter(id=user.id).count())


@rules.predicate
def is_account_manager(user, account=None):
    if account is None:
        return bool(Policy.objects.filter(managers=user).count())
    else:
        if hasattr(account, 'policy'):
            return is_policy_manager(user, account.policy)


rules.add_perm('subscription.manage_policy',
               is_authenticated & (is_superuser | is_staff | is_policy_manager))
rules.add_perm('subscription.manage_account',
               is_authenticated & (is_superuser | is_staff | is_account_manager))
