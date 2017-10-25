# -*- coding: utf-8 -*-

from django.conf import settings


def common_settings(request):
    """ Passing custom CONSTANT in Settings into RequestContext. """
    COMMON_CONTEXT = {
        'MAILCHIMP_UUID': settings.MAILCHIMP_UUID,
        'MAILCHIMP_ACTION_URL': settings.MAILCHIMP_ACTION_URL,
    }

    if hasattr(settings, 'ANALYTICS_TRACKING_CODES'):
        COMMON_CONTEXT['ANALYTICS_TRACKING_CODES'] = settings.ANALYTICS_TRACKING_CODES

    try:
        # set EXTRA_CONTEXT in local settings
        COMMON_CONTEXT.update(settings.EXTRA_CONTEXT)
    except AttributeError:
        pass

    if settings.DEBUG:
        COMMON_CONTEXT.update({
            "WEBPACK_DEV_SERVER_URL": getattr(settings, 'WEBPACK_DEV_SERVER_URL', ''),
        })

    return COMMON_CONTEXT


def cache_constants(request):
    """ Returns some cache timeout that can be used to perform fragment caching in templates.

    These timeouts can be used to do russian doll caching in templates by nesting cache calls with
    different expirations.
    """
    return {
        'SHORT_TTL': 600,       # 10 minutes
        'MIDDLE_TTL': 1800,     # 30 minutes
        'LONG_TTL': 3600,       # 1 hour
        'FOREVER_TTL': 604800,  # 7 days
    }
