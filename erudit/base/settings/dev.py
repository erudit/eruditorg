# -*- coding: utf-8 -*-

from .base import *  # noqa

DEBUG = True

ALLOWED_HOSTS = [
    'localhost:8000',
]

INTERNAL_IPS = (
    '127.0.0.1',
)

STATICFILES_DIRS = (
    str(ROOT_DIR / 'erudit' / 'static' / 'build_dev'),
    str(ROOT_DIR / 'erudit' / 'static' / 'build'),
    str(ROOT_DIR / 'erudit' / 'static'),
)

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

INSTALLED_APPS += (
    'debug_toolbar',
)
