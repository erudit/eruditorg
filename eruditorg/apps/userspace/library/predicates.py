import rules
from erudit.models.core import Organisation


@rules.predicate
def is_organisation_member(user, organisation=None):
    if organisation is None:
        return bool(Organisation.objects.filter(members=user).count())
    else:
        return bool(organisation.members.filter(id=user.id).count())
