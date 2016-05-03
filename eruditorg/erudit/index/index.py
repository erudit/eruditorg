# -*- coding: utf-8 -*-

from elasticsearch import Elasticsearch

from .conf import settings as index_settings
from .mappings import MAPPINGS


INDEX_CONFIGURATION = {
    'settings': {
        'number_of_shards': index_settings.ES_INDEX_NUMBER_OF_SHARDS,
        'number_of_replicas': index_settings.ES_INDEX_NUMBER_OF_REPLICAS,
        # We define here a "folding" filter in order to convert alphabetic, numeric, and symbolic
        # Unicode characters into their ASCII equivalents. We use the "preserve_original" option in
        # order to index original tokens and folded tokens. But perhaps explicit sub-fields using
        # the "folding" filter should be created as stated in the Elasticsearch documentation. See:
        # https://www.elastic.co/guide/en/elasticsearch/guide/current/asciifolding-token-filter.html
        'analysis': {
            'analyzer': {
                'default': {
                    'tokenizer': 'standard',
                    'filter': ['standard', 'folding', ],
                },
                'sort': {
                    'type': 'custom',
                    'tokenizer': 'keyword',
                    'filter':  ['lowercase', 'asciifolding', ],
                    # TODO: Should we define 'stopwords' here?
                },
            },
            'filter': {
                'folding': {
                    'type': 'asciifolding',
                    'preserve_original': True,
                }
            }
        },
    },
    'mappings': MAPPINGS,
}


def get_client():
    """ Returns an Elasticsearch objects and ensures that the Érudit index is created. """
    client = Elasticsearch(index_settings.ES_HOSTS)
    if not client.indices.exists(index_settings.ES_INDEX_NAME):
        # The index is not created, so we should ensure it is created before going further!
        client.indices.create(index=index_settings.ES_INDEX_NAME, body=INDEX_CONFIGURATION)
    return client
