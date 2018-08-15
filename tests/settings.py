import os

from base.settings.base import *  # noqa

DEBUG = True

class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return 'notmigrations'

TEST_ROOT = os.path.abspath(os.path.dirname(__file__))

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
    },
    'files': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    'fedora': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Not an actual setting, but can be used in some tests with @override_settings
NO_CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache'
    },
    'files': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    },
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    },
}

DATABASE_ROUTERS = [
    'core.subscription.restriction.router.RestrictionRouter',
]

RESTRICTION_MODELS_ARE_MANAGED = True

MANAGED_COLLECTIONS = ('erudit',)

MEDIA_ROOT = os.path.join(TEST_ROOT, '_testdata/media/')

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

INSTALLED_APPS = list(INSTALLED_APPS)
INSTALLED_APPS.remove('raven.contrib.django.raven_compat')
INSTALLED_APPS.append('core.subscription.restriction')
INSTALLED_APPS.append('tests')

FALLBACK_BASE_URL = 'https://retro.erudit.org/'

MIGRATION_MODULES = DisableMigrations()

USE_DEBUG_EMAIL = False

METRICS_ACTIVATED = True
TRACKING_INFLUXDB_HOST = 'localhost'
TRACKING_INFLUXDB_PORT = 8086
TRACKING_INFLUXDB_DBNAME = 'erudit-metrics'
TRACKING_INFLUXDB_USER = 'root'
TRACKING_INFLUXDB_PASSWORD = 'root'

FEDORA_ROOT = 'http://erudit.org'
SOLR_ROOT = 'http://erudit.org'

POST_OFFICE = {
    'DEFAULT_PRIORITY': 'now',
}

EDITOR_MAIN_PRODUCTION_TEAM_IDENTIFIER = 'main'
