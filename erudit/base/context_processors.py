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
        "DEBUG": settings.DEBUG,
        "HOSTNAME": HOSTNAME,
        "CURRENT_DOMAIN": get_current_site(request).domain,
    }

    try:
        # set EXTRA_CONTEXT in local settings
        COMMON_CONTEXT.update(settings.EXTRA_CONTEXT)
    except:
        pass

    return COMMON_CONTEXT
