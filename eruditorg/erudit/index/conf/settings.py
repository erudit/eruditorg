# -*- coding: utf-8 -*-

from django.conf import settings


ES_HOSTS = getattr(settings, 'ERUDIT_ES_HOSTS', ['localhost:9200', ])

ES_INDEX_NAME = getattr(settings, 'ERUDIT_ES_INDEX_NAME', 'eruditdocuments')
ES_INDEX_DOC_TYPE = getattr(settings, 'ERUDIT_ES_INDEX_DOC_TYPE', 'eruditdocument')

# Defines the settings associated with the index of Érudit documents
ES_INDEX_SETTINGS = getattr(settings, 'ERUDIT_ES_INDEX_SETTINGS', {
    'number_of_shards': 5,
    'number_of_replicas': 1,
    # We define here a "folding" filter in order to convert alphabetic, numeric, and symbolic
    # Unicode characters into their ASCII equivalents. We use the "preserve_original" option in
    # order to index original tokens and folded tokens. But perhaps explicit sub-fields using the
    # "folding" filter should be created as stated in the Elasticsearch documentation. See:
    # https://www.elastic.co/guide/en/elasticsearch/guide/current/asciifolding-token-filter.html
    'analysis': {
        'analyzer': {
            'default': {
                'tokenizer': 'standard',
                'filter': ['standard', 'folding', ],
            }
        },
        'filter': {
            'folding': {
                'type': 'asciifolding',
                'preserve_original': True,
            }
        }
    }
})
