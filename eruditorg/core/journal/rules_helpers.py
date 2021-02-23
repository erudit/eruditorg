from django.db.models import Q

from erudit.models import Journal
from erudit.models import Organisation


def get_editable_journals(user):
    """ Given a specific user, returns all the Journal instances he can edit. """

    if user.is_superuser or user.is_staff:
        return Journal.managed_objects.all()

    # Check if the given user is a member of a production team group.
    production_team_group = user.groups.filter(productionteam__isnull=False)
    if production_team_group.exists():
        # Get the journals for which the user is a member or the journals of the production team.
        return Journal.objects.filter(
            Q(members=user) | Q(productionteam__group__in=production_team_group)
        )

    # TODO: add proper permissions checks
    return Journal.objects.filter(members=user)


def get_editable_organisations(user):
    """ Given a specific user, returns all the Organisation instances he can edit. """
    if user.is_superuser or user.is_staff:
        return Organisation.objects.all()
    # TODO: add proper permissions checks
    return user.organisations.all()
