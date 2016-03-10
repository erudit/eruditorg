# -*- coding: utf-8 -*-

from django.conf import settings


PRODUCTION_TEAM_GROUP_ID = getattr(settings, 'PRODUCTION_TEAM_GROUP_ID', 1)
