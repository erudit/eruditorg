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

    COMMON_CONTEXT.update({
        'ISSUE_COVERPAGE_AVERAGE_SIZE': settings.ISSUE_COVERPAGE_AVERAGE_SIZE,
        'JOURNAL_LOGO_AVERAGE_SIZE': settings.JOURNAL_LOGO_AVERAGE_SIZE,
    })

    return COMMON_CONTEXT


def cache_constants(request):
    """ Returns some cache timeout that can be used to perform fragment caching in templates.

    These timeouts can be used to do russian doll caching in templates by nesting cache calls with
    different expirations.
    """
    return {
        'NEVER_TTL': settings.NEVER_TTL,        # Do not cache
        'SHORT_TTL': settings.SHORT_TTL,        # Cache for 1 hour
        'LONG_TTL': settings.LONG_TTL,          # Cache for 1 day
        'FOREVER_TTL': settings.FOREVER_TTL,    # Cache forever
    }
