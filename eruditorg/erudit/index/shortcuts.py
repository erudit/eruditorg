# -*- coding: utf-8 -*-

from .conf import settings as index_settings


def index(client, body, erudit_document):
    """ Adds or updates a single document to the Érudit index. """
    client.index(
        index=index_settings.ES_INDEX_NAME, doc_type=index_settings.ES_INDEX_DOC_TYPE,
        id=erudit_document.localidentifier, body=body)
