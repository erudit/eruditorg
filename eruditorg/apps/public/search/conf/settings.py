# -*- coding: utf-8 -*-

from django.conf import settings


DEFAULT_PAGE_SIZE = getattr(settings, "SEARCH_DEFAULT_PAGE_SIZE", 10)
MAX_ADVANCED_PARAMETERS = getattr(settings, "SEARCH_MAX_ADVANCED_PARAMETERS", 10)

MAX_SAVED_SEARCHES = getattr(settings, "SEARCH_MAX_SAVED_SEARCHES", 10)
