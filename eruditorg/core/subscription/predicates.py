import rules

from core.subscription.models import Organisation


@rules.predicate
def can_manage_an_organisation(user):
    return is_organisation_member(user)


@rules.predicate
def is_organisation_member(user, organisation=None):
    if organisation is None:
        return bool(Organisation.objects.filter(members=user).count())
    else:
        return bool(organisation.members.filter(id=user.id).count())
