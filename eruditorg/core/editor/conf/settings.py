# -*- coding: utf-8 -*-

from django.conf import settings


MAIN_PRODUCTION_TEAM_IDENTIFIER = getattr(
    settings, 'EDITOR_MAIN_PRODUCTION_TEAM_IDENTIFIER', 'main')
