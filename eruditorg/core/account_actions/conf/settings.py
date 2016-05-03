# -*- coding: utf-8 -*-

from django.conf import settings


# Use this setting to specify a duration of validation for action tokens. This duration should be
# expressed as a number of days.
ACTION_TOKEN_VALIDITY_DURATION = getattr(settings, 'ACTION_TOKEN_VALIDITY_DURATION', 10)
