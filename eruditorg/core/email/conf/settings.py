# -*- coding: utf-8 -*-

from django.conf import settings


DEBUG_EMAIL_ADDRESS = getattr(settings, "DEBUG_EMAIL_ADDRESS", "django-test@erudit.dummy")
USE_DEBUG_EMAIL = getattr(settings, "USE_DEBUG_EMAIL", settings.DEBUG)
