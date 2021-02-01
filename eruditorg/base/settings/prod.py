from .base import *  # noqa

import structlog

from structlog_sentry import SentryJsonProcessor


FALLBACK_BASE_URL = 'https://retro.erudit.org/'

# Metrics
# -----------------------------------------------------------------------------
METRICS_ACTIVATED = False
# METRICS_INFLUXDB_HOST = "{{ influxdb_host }}"
# METRICS_INFLUXDB_PORT = "{{ influxdb_port }}"
# METRICS_INFLUXDB_DBNAME = "{{ influxdb_dbname }}"
# METRICS_INFLUXDB_USER = "{{ influxdb_user }}"
# METRICS_INFLUXDB_PASSWORD = "{{ influxdb_password }}"

# Content providers
# -----------------------------------------------------------------------------

DJANGO_LOG_DIRECTORY = env('DJANGO_LOG_DIRECTORY')

# Journals

ERUDIT_JOURNAL_PROVIDERS = {
    'fedora': [
        {
            'collection_title': 'Érudit',
            'collection_code': 'erudit',
            'localidentifier': 'erudit',
        },
        {
            'collection_title': 'The Electronic Text Centre at UNB Libraries',
            'collection_code': 'unb',
            'localidentifier': 'unb',
        },
    ],
    'oai': [
        {
            'collection_title': 'Persée',
            'collection_code': 'persee',
            'endpoint': 'http://oai.persee.fr/oai',
            'issue_metadataprefix': 'persee_mets',
        },
    ],
}

# Thesis

ERUDIT_THESIS_PROVIDERS = {
    'oai': [

        {
            'collection_title': 'Université de Montréal',
            'collection_code': 'udem',
            'endpoint': 'http://papyrus.bib.umontreal.ca/oai/request',
            'sets': ['col_1866_2621', ],
        },
        {
            'collection_title': 'McGill University',
            'collection_code': 'mcgill',
            'endpoint': 'http://digitool.library.mcgill.ca/OAI-PUB',
            'sets': ['eTheses', ],
        },
        {
            'collection_title': 'Université Laval',
            'collection_code': 'laval',
            'endpoint': 'http://www.theses.ulaval.ca:8080/oaicat/servlet/OAIHandler',
        },
        {
            'collection_title': 'Université du Québec à Montréal',
            'collection_code': 'uqam',
            'endpoint': 'http://www.archipel.uqam.ca/cgi/oai2-etdms',
            'sets': ['74797065733D6D6173746572', '74797065733D746865736973', ],
        },
        {
            'collection_title': 'Université du Québec à Chicoutimi',
            'collection_code': 'uqac',
            'endpoint': 'http://constellation.uqac.ca/cgi/oai2-etdms',
            'sets': ['74797065733D746865736973', ],
        },
        {
            'collection_title': 'Université du Québec à Trois-Rivières',
            'collection_code': 'uqtr',
            'endpoint': 'http://depot-e.uqtr.ca/cgi/oai2-etdms',
            'sets': ['74797065733D746865736973', ],
        },
        {
            'collection_title': 'Université du Québec en Abitibi-Témiscamingue',
            'collection_code': 'uqat',
            'endpoint': 'http://depositum.uqat.ca/cgi/oai2-etdms',
            'sets': ['74797065733D746865736973', ],
        },
        {
            'collection_title': 'Université du Québec à Rimouski',
            'collection_code': 'uqar',
            'endpoint': 'http://semaphore.uqar.ca/cgi/oai2-etdms',
            'sets': ['74797065733D746865736973', ],
        },
        {
            'collection_title': "École nationale d'administration publique",
            'collection_code': 'enap',
            'endpoint': 'http://espace.enap.ca/cgi/oai2-etdms',
            'sets': ['74797065733D746865736973', ],
        },
        {
            'collection_title': "Institut national de recherche scientifique",

            'collection_code': 'inrs',
            'endpoint': 'http://espace.inrs.ca/cgi/oai2-etdms',
            'sets': ['74797065733D746865736973', ],
        },
        {
            'collection_title': "Polytechnique Montréal",
            'collection_code': 'polymtl',
            'endpoint': 'https://publications.polymtl.ca/cgi/oai2',
            'sets': ['erudit'],
        },

    ],
}

SOLR_TIMEOUT = 15


# Logging
# -----------------------------------------------------------------------------

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'WARNING',
        'handlers': ['console'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(process)d %(thread)d %(message)s'
        },
        'structlog': {
            'format': '%(levelname)s %(message)s'
        },
        'userspace.journal.editor': {
            'format': '{"level": "%(levelname)s", "time": "%(asctime)s", "username": "%(username)s", "journal_code": "%(journal_code)s", "message": "%(message)s", "issue_submission": "%(issue_submission)s"}'  # noqa
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'structlog'
        },

        'cron_console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },

        'userspace.journal.editor.console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'userspace.journal.editor'
        },

        'userspace.journal.editor.file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': DJANGO_LOG_DIRECTORY + '/userspace.journal.editor.log',
            'maxBytes': 1024 * 1024 * 1,
            'backupCount': 5,
            'formatter': 'userspace.journal.editor',
        },
        'import_journals_from_fedora': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': DJANGO_LOG_DIRECTORY + '/import_journals_from_fedora.log',
            'maxBytes': 1024 * 1024 * 1,
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'import_institution_subscriptions': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': DJANGO_LOG_DIRECTORY + '/import_institution_subscriptions.log',
            'maxBytes': 1024 * 1024 * 1,
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'import_individual_subscriptions': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': DJANGO_LOG_DIRECTORY + '/import_individual_subscriptions.log',
            'formatter': 'structlog',
        },
        'article_access': {
            'level': 'DEBUG',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': DJANGO_LOG_DIRECTORY + '/www.erudit.org.article_access.log',
            'formatter': 'structlog',
        },
        'referer': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'midnight',
            'filename': DJANGO_LOG_DIRECTORY + '/www.erudit.org.referer.log',
            'formatter': 'verbose',
        },
        'fedora_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': DJANGO_LOG_DIRECTORY + '/fedora.log',
            'maxBytes': 1024 * 1024 * 1,
            'backupCount': 5,
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'root': {
            'level': 'WARNING',
            'handlers': ['console'],
        },
        'gunicorn': {
            'level': 'INFO',
            'handlers': ['console'],
        },
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'apps.public.journal.viewmixins': {
            'level': 'INFO',
            'handlers': ['article_access', ],
            'propagate': False,
        },
        'apps.userspace.journal.editor.views': {
            'level': 'DEBUG',
            'handlers': ['userspace.journal.editor.file', ],
            'propagate': False,
        },
        'erudit.management.commands.import_journals_from_fedora': {
            'level': 'INFO',
            'handlers': ['import_journals_from_fedora', ],
            'propagate': False,
        },
        'core.subscription.management.commands.import_restrictions': {
            'level': 'INFO',
            'handlers': ['import_institution_subscriptions', ],
            'propagate': False,
        },
        'core.subscription.management.commands.import_individual_subscriptions': {
            'level': 'INFO',
            'handlers': ['import_individual_subscriptions', ],
            'propagate': False,
        },
        'core.subscription.middleware': {
            'level': 'INFO',
            'handlers': ['referer', 'console', ],
            'propagate': False,
        },
        'erudit.fedora': {
            'level': 'INFO',
            'handlers': ['fedora_file', ],
            'propagate': False,
        },
        'post_office': {
            'level': 'ERROR',
            'handlers': ['cron_console', ],
            'propagate': False,
        }
    },
}

structlog.configure(
    logger_factory=LoggerFactory(),
    processors=[
        structlog.processors.format_exc_info,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        SentryJsonProcessor(level=logging.ERROR),
        structlog.processors.JSONRenderer(sort_keys=True),
    ]
)

# must be here in `prod.py` because some code tests for the existence of these settings
FIXTURE_ROOT = env('FIXTURE_ROOT')
JOURNAL_FIXTURES = env('FIXTURE_ROOT')
RESTRICTION_ABONNE_ICONS_PATH = env('RESTRICTION_ABONNE_ICONS_PATH')


ANALYTICS_HOTJAR_TRACKING_CODE = env('ANALYTICS_HOTJAR_TRACKING_CODE')
ANALYTICS_GOOGLE_TRACKING_CODE = env('ANALYTICS_GOOGLE_TRACKING_CODE')

ANALYTICS_TRACKING_CODES = [tc for tc in
                            [ANALYTICS_HOTJAR_TRACKING_CODE, ANALYTICS_GOOGLE_TRACKING_CODE] if tc]
