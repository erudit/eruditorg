# -*- coding: utf-8 -*-

from django.conf import settings


ES_HOSTS = getattr(settings, 'ERUDIT_ES_HOSTS', ['localhost:9200', ])

ES_INDEX_NAME = getattr(settings, 'ERUDIT_ES_INDEX_NAME', 'eruditdocuments')
ES_INDEX_DOC_TYPE = getattr(settings, 'ERUDIT_ES_INDEX_DOC_TYPE', 'eruditdocument')
ES_INDEX_NUMBER_OF_SHARDS = getattr(settings, 'ERUDIT_ES_INDEX_NUMBER_OF_SHARDS', 5)
ES_INDEX_NUMBER_OF_REPLICAS = getattr(settings, 'ERUDIT_ES_INDEX_NUMBER_OF_REPLICAS', 1)
