# -*- coding: utf-8 -*-

import logging

from django.contrib.auth.models import Group

from .conf import settings as editor_settings

logger = logging.getLogger(__name__)


def get_production_team_group():
    """ Returns the Django group related to the production team. """
    try:
        production_team = Group.objects.get(id=editor_settings.PRODUCTION_TEAM_GROUP_ID)
    except Group.DoesNotExist:  # pragma: no cover
        logger.error('Unable to find production team group with ID {}'.format(
            editor_settings.PRODUCTION_TEAM_GROUP_ID), exc_info=True)
        production_team = None
    return production_team
