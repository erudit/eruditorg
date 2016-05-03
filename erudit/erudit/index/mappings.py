# -*- coding: utf-8 -*-

"""
Defines the mappings used to create the index of Érudit documents.

For reference, see: https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping.html
"""

from .conf import settings as index_settings


MAPPINGS = {
    index_settings.ES_INDEX_DOC_TYPE: {
        'properties': {
            'localidentifier': {
                'type': 'string',
                'store': True,
                'copy_to': ['all', 'meta', ],
            },
            'publication_year': {'type': 'string'},
            'number': {'type': 'string'},
            'issn': {
                'type': 'string',
                'copy_to': ['all', 'meta', ],
            },
            'isbn': {'type': 'string'},
            'authors': {
                'type': 'string',
                'position_increment_gap': 100,
                'copy_to': ['all', 'meta', ],
            },
        }
    }
}
