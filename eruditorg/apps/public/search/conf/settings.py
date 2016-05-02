# -*- coding: utf-8 -*-

from django.conf import settings


MAX_ADVANCED_PARAMETERS = getattr(settings, 'SEARCH_MAX_ADVANCED_PARAMETERS', 10)
