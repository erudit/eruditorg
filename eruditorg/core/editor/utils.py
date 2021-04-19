import datetime as dt

from django.contrib.auth.models import Group
from django.db.models.query import QuerySet

from core.editor.conf import settings as editor_settings
from erudit.models.journal import Journal


def get_archive_date(validation_date):
    return validation_date + dt.timedelta(days=editor_settings.ARCHIVAL_DAY_OFFSET)


def get_production_teams_groups(journal: Journal) -> QuerySet:
    """Returns the production teams groups associated with the provided journal.

    If no production team group is associated with the provided journal, returns the main
    production team group.
    """
    production_teams_groups = Group.objects.filter(productionteam__journals__id=journal.id)

    if not production_teams_groups.count():
        production_teams_groups = Group.objects.filter(
            productionteam__identifier=editor_settings.MAIN_PRODUCTION_TEAM_IDENTIFIER
        )

    return production_teams_groups
