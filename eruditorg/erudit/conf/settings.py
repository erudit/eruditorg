# -*- coding: utf-8 -*-

from django.conf import settings


# The FEDORA_COLLECTIONS setting defines the collections whose journals can be retrieved using the
# Fedora repository. It should be a list of collection codes.
DEFAULT_FEDORA_COLLECTIONS = ['erudit', ]
FEDORA_COLLECTIONS = getattr(settings, 'ERUDIT_FEDORA_COLLECTIONS', DEFAULT_FEDORA_COLLECTIONS)
