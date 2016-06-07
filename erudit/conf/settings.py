# -*- coding: utf-8 -*-

from django.conf import settings


# Fedora credentials
FEDORA_ROOT = getattr(settings, 'ERUDIT_FEDORA_ROOT', None) \
    or getattr(settings, 'FEDORA_ROOT', None) \
    or 'http://localhost:8080/fedora/'
FEDORA_USER = getattr(settings, 'ERUDIT_FEDORA_USER', None) \
    or getattr(settings, 'FEDORA_USER', None)\
    or 'fedoraAdmin'
FEDORA_PASSWORD = getattr(settings, 'ERUDIT_FEDORA_PASSWORD', None) \
    or getattr(settings, 'FEDORA_PASSWORD', None) \
    or 'fedoraAdmin'

FEDORA_PIDSPACE = getattr(settings, 'ERUDIT_FEDORA_PIDSPACE', 'erudit')
FEDORA_XML_CONTENT_CACHE_TIMEOUT = getattr(
    settings, 'ERUDIT_FEDORA_XML_CONTENT_CACHE_TIMEOUT', 60 * 60)
FEDORA_FILEBASED_CACHE_NAME = getattr(settings, 'ERUDIT_FEDORA_FILEBASED_CACHE_NAME', 'files')


# The FEDORA_COLLECTIONS setting defines the collections whose journals can be retrieved using the
# Fedora repository. It should be a list of collection codes.
DEFAULT_FEDORA_COLLECTIONS = ['erudit', ]
FEDORA_COLLECTIONS = getattr(settings, 'ERUDIT_FEDORA_COLLECTIONS', DEFAULT_FEDORA_COLLECTIONS)

# The OAI_PROVIDERS setting defines the OAI providers whose sets are imported as Journal instances.
# Each provider should be defined as follows:
#
#     {
#         'collection_code': {
#             'name': 'Collection name',
#             'endpoint': '[OAI-PMH endpoint URL]',
#         },
#     }
DEFAULT_OAI_PROVIDERS = {
    'persee': {
        'name': 'Persée',
        'endpoint': 'http://oai.persee.fr/oai',
    },
}
OAI_PROVIDERS = getattr(settings, 'ERUDIT_OAI_PROVIDERS', DEFAULT_OAI_PROVIDERS)
