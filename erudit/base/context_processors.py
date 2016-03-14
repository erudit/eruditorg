from __future__ import unicode_literals

import socket
from django.conf import settings

try:
    HOSTNAME = socket.gethostname()
except:
    HOSTNAME = 'localhost'


def common_settings(request):
    """Passing custom CONSTANT in Settings into RequestContext."""
    from django.contrib.sites.models import get_current_site
    COMMON_CONTEXT = {
        "MAILCHIMP_UUID": settings.MAILCHIMP_UUID,
        "MAILCHIMP_ACTION_URL": settings.MAILCHIMP_ACTION_URL,
        "HOSTNAME": HOSTNAME,
        "CURRENT_DOMAIN": get_current_site(request).domain,
    }

    try:
        # set EXTRA_CONTEXT in local settings
        COMMON_CONTEXT.update(settings.EXTRA_CONTEXT)
    except:
        pass

    if settings.DEBUG:
        COMMON_CONTEXT.update({
            "WEBPACK_DEV_SERVER_URL": getattr(settings, 'WEBPACK_DEV_SERVER_URL', ''),
        })

    return COMMON_CONTEXT
