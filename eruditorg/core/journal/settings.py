from django.conf import settings
MANAGED_COLLECTIONS = getattr(settings, 'MANAGED_COLLECTIONS', tuple())
