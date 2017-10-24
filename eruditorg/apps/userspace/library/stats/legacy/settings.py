from django.conf import settings

ERUDIT_COUNTER_BACKEND_URL = getattr(
    settings, 'ERUDIT_COUNTER_BACKEND_URL', "http://counter-backend.localhost"
)
