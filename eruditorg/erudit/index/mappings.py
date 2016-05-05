# -*- coding: utf-8 -*-

"""
Defines the mappings used to create the index of Érudit documents.

For reference, see: https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping.html
"""

from .conf import settings as index_settings


# We will define custom _all fields using the 'copy_to' option. These fields can be used to perform
# powerfull searches on the Érudit documents' index.
ALL = 'all'
META = 'meta'
TITLE_ABSTRACT_KEYWORDS = 'title_abstract_keywords'
ISSN_FULL = 'issn_full'
ISBN_FULL = 'isbn_full'


MAPPINGS = {
    index_settings.ES_INDEX_DOC_TYPE: {
        'properties': {
            'localidentifier': {
                'type': 'string',
                'store': True,
                'copy_to': [ALL, META, ],
            },
            'publication_date': {'type': 'date'},
            'publication_year': {'type': 'string'},
            'number': {'type': 'string'},
            'issn': {
                'type': 'string',
                'copy_to': [ALL, META, ISSN_FULL, ],
            },
            'issn_num': {
                'type': 'string',
                'copy_to': [ALL, META, ISSN_FULL, ],
            },
            'isbn': {
                'type': 'string',
                'copy_to': [ALL, META, ISBN_FULL, ],
            },
            'isbn_num': {
                'type': 'string',
                'copy_to': [ALL, META, ISBN_FULL, ],
            },
            'authors': {
                'type': 'string',
                'position_increment_gap': 100,
                'copy_to': [ALL, 'author', ],
                'fields': {
                    'sort': {
                        'type': 'string',
                        'analyzer': 'sort',
                    },
                    'raw': {
                        'type': 'string',
                        'index': 'not_analyzed',
                    },
                },
            },
            'author_affiliations': {
                'type': 'string',
                'position_increment_gap': 100,
                'copy_to': [ALL, META, ],
            },
            'keywords': {
                'type': 'string',
                'position_increment_gap': 100,
                'copy_to': [ALL, TITLE_ABSTRACT_KEYWORDS, ],
            },
            'abstracts': {
                'type': 'string',
                'copy_to': [ALL, TITLE_ABSTRACT_KEYWORDS, ],
            },
            'title': {
                'type': 'string',
                'copy_to': [ALL, TITLE_ABSTRACT_KEYWORDS, ],
                'fields': {
                    'sort': {
                        'type': 'string',
                        'analyzer': 'sort',
                    },
                },
            },
            'subtitle': {
                'type': 'string',
                'copy_to': [ALL, TITLE_ABSTRACT_KEYWORDS, ],
            },
            'text': {
                'type': 'string',
                'copy_to': [ALL, ],
            },
            'refbiblios': {
                'type': 'string',
                'copy_to': [ALL, META, ],
            },
            'trefbiblios': {
                'type': 'string',
                'copy_to': [ALL, META, ],
            },
            'article_type': {
                'type': 'string',
            },
            'lang': {
                'type': 'string',
            },
            'collection': {
                'type': 'string',
                'copy_to': [ALL, META, ],
                'fields': {
                    'raw': {
                        'type': 'string',
                        'index': 'not_analyzed',
                    },
                },
            },
            'fund': {
                'type': 'string',
                'fields': {
                    'raw': {
                        'type': 'string',
                        'index': 'not_analyzed',
                    },
                },
            },
            'corpus': {
                'type': 'string',
                'fields': {
                    'raw': {
                        'type': 'string',
                        'index': 'not_analyzed',
                    },
                },
            },
            'theme': {
                'type': 'string',
                'copy_to': [ALL, TITLE_ABSTRACT_KEYWORDS, ],
            },
        }
    }
}
