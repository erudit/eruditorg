# -*- coding: utf-8 -*-

from elasticsearch import Elasticsearch

from .conf import settings as index_settings
from .mappings import MAPPINGS


def get_client():
    """ Returns an Elasticsearch objects and ensures that the Érudit index is created. """
    client = Elasticsearch(index_settings.ES_HOSTS)
    if not client.indices.exists(index_settings.ES_INDEX_NAME):
        # The index is not created, so we should ensure it is created before going further!
        request_body = {'settings': index_settings.ES_INDEX_SETTINGS, 'mappings': MAPPINGS}
        client.indices.create(index=index_settings.ES_INDEX_NAME, body=request_body)
    return client
