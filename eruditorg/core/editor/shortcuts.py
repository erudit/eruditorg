# -*- coding: utf-8 -*-

import logging

from .conf import settings as editor_settings
from .models import ProductionTeam

logger = logging.getLogger(__name__)


def get_production_team_group(journal=None):
    """ Returns the group related to the production team associated with the given journal. """
    try:
        production_team = ProductionTeam.objects.get(
            identifier=editor_settings.MAIN_PRODUCTION_TEAM_IDENTIFIER) if journal is None \
            else ProductionTeam.objects.filter(journals__id=journal.id).first()
        production_team = production_team or ProductionTeam.objects.get(
            identifier=editor_settings.MAIN_PRODUCTION_TEAM_IDENTIFIER)
        production_team_group = production_team.group
    except ProductionTeam.DoesNotExist:  # pragma: no cover
        logger.error('Unable to find the main production team group with identifier {}'.format(
            editor_settings.MAIN_PRODUCTION_TEAM_IDENTIFIER), exc_info=True)
        production_team_group = None
    return production_team_group


def is_production_team_member(user):
    """ Returns a boolean indicating if the given user is a member of a production team. """
    return user.groups.filter(productionteam__isnull=False)
