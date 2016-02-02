import rules


@rules.predicate
def is_superuser(user):
    return user.is_superuser


@rules.predicate
def is_staff(user):
    return user.is_staff
