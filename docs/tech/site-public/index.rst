Import des revues
=================

Import depuis fedora
--------------------

    ::

        python manage.py import_journals_from_fedora

Import depuis OAI
-----------------

Configurer les fournisseurs de revues OAI dans les settings. Par exemple:

    ::

        ERUDIT_JOURNAL_PROVIDERS = {
            'oai': [
                {
                    'collection_title': 'Ma collection',
                    'collection_code': 'macollection',
                    'endpoint': 'http://macollection.ca/
                    'issue_metadataprefix': 'macollection'
                }
            ]
        }

Importer les revues des fournisseurs:

    ::

        python manage.py import_journals_from_oai
