# -*- coding: utf-8 -*-

from .base import *  # noqa

DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
]

INTERNAL_IPS = (
    '127.0.0.1',
)

STATICFILES_DIRS = (
    str(ROOT_DIR / 'eruditorg' / 'static' / 'build_dev'),
    str(ROOT_DIR / 'eruditorg' / 'static' / 'build'),
    str(ROOT_DIR / 'eruditorg' / 'static'),
)

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

MIDDLEWARE += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

INSTALLED_APPS += (
    'debug_toolbar',
    'debug_toolbar_line_profiler',
    'template_timings_panel',
    'djcelery',
    'kombu.transport.django',
)

TEMPLATES[0]['OPTIONS']['loaders'] = [
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
]

BROKER_URL = 'django://'
CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'

DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
)

# Copy these lines into your ``settings_env`` module and uncomment them
# in order to use hot reloading!

# WEBPACK_DEV_SERVER_URL = 'http://localhost:8080'
