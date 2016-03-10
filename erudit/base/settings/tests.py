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

INSTALLED_APPS = list(INSTALLED_APPS)
INSTALLED_APPS.remove('raven.contrib.django.raven_compat')

MIGRATION_MODULES = DisableMigrations()

USE_DEBUG_EMAIL = False
