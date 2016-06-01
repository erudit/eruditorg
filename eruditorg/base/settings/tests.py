# -*- coding: utf-8 -*-

from .base import *  # noqa


class DisableMigrations(object):
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return 'notmigrations'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
}

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

INSTALLED_APPS = list(INSTALLED_APPS)
INSTALLED_APPS.remove('raven.contrib.django.raven_compat')

MIGRATION_MODULES = DisableMigrations()

USE_DEBUG_EMAIL = False

TRACKING_INFLUXDB_HOST = 'localhost'
TRACKING_INFLUXDB_PORT = 8086
TRACKING_INFLUXDB_DBNAME = 'erudit-metrics'
TRACKING_INFLUXDB_USER = 'root'
TRACKING_INFLUXDB_PASSWORD = 'root'
