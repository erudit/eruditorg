import rules
from rules.predicates import is_staff, is_superuser

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
        return is_policy_manager(user, account.policy)

rules.add_perm('individual_subscription.manage_policy',
               is_superuser | is_staff | is_policy_manager)
rules.add_perm('individual_subscription.manage_account',
               is_superuser | is_staff | is_account_manager)
