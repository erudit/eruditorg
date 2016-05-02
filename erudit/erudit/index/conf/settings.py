# -*- coding: utf-8 -*-

from django.conf import settings


ES_HOSTS = getattr(settings, 'ERUDIT_ES_HOSTS', ['localhost:9200', ])

ES_INDEX_NAME = getattr(settings, 'ERUDIT_ES_INDEX_NAME', 'eruditdocuments')
ES_INDEX_DOC_TYPE = getattr(settings, 'ERUDIT_ES_INDEX_DOC_TYPE', 'eruditdocument')

# Defines the settings associated with the index of Érudit documents
ES_INDEX_SETTINGS = getattr(settings, 'ERUDIT_ES_INDEX_SETTINGS', {
    'number_of_shards': 5,
    'number_of_replicas': 1,
})
