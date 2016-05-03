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
            'publication_date': {'type': 'date'},
            'publication_year': {'type': 'string'},
            'number': {'type': 'string'},
            'issn': {
                'type': 'string',
                'copy_to': ['all', 'meta', ],
            },
            'issn_num': {
                'type': 'string',
                'copy_to': ['all', 'meta', ],
            },
            'isbn': {
                'type': 'string',
                'copy_to': ['all', 'meta', ],
            },
            'isbn_num': {
                'type': 'string',
                'copy_to': ['all', 'meta', ],
            },
            'authors': {
                'type': 'string',
                'position_increment_gap': 100,
                'copy_to': ['all', ],
                'fields': {
                    'sort': {
                        'type': 'string',
                        'analyzer': 'sort',
                    },
                },
            },
            'author_affiliations': {
                'type': 'string',
                'position_increment_gap': 100,
                'copy_to': ['all', 'meta', ],
            },
            'keywords': {
                'type': 'string',
                'position_increment_gap': 100,
                'copy_to': ['all', ],
            },
            'abstracts': {
                'type': 'string',
                'copy_to': ['all', ],
            },
            'title': {
                'type': 'string',
                'copy_to': ['all', ],
                'fields': {
                    'sort': {
                        'type': 'string',
                        'analyzer': 'sort',
                    },
                },
            },
            'subtitle': {
                'type': 'string',
                'copy_to': ['all', ],
            },
            'text': {
                'type': 'string',
                'copy_to': ['all', ],
            },
            'refbiblios': {
                'type': 'string',
                'copy_to': ['all', 'meta', ],
            },
        }
    }
}
