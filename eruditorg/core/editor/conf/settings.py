# -*- coding: utf-8 -*-

from django.conf import settings


MAIN_PRODUCTION_TEAM_IDENTIFIER = getattr(
    settings, 'EDITOR_MAIN_PRODUCTION_TEAM_IDENTIFIER', 'main')


# Number of days after which validated issue submissions will be archived and their files will be
# deleted.
ARCHIVAL_DAY_OFFSET = 90

# Number of days with no activity on issue submissions after which we notify the production team by
# email that an action is needed.
ACTION_NEEDED_DAY_OFFSET = 14
