import rules

from userspace.rules import is_superuser, is_staff

from .models import Policy


@rules.predicate
def can_manage_policy(user, policy=None):
    if policy is None:
        return bool(Policy.objects.filter(managers=user).count())
    else:
        return bool(policy.managers.filter(id=user.id).count())


@rules.predicate
def can_manage_account(user, account=None):
    if account is None:
        return bool(Policy.objects.filter(managers=user).count())
    else:
        return can_manage_policy(user, account.policy)

rules.add_perm('individual_subscription.manage_policy', is_superuser | is_staff | can_manage_policy)
rules.add_perm('individual_subscription.manage_account', is_superuser | is_staff | can_manage_account)
