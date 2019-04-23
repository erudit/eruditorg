from .base import *  # noqa

ACTIVATE_DEBUG_TOOLBAR = env("ACTIVATE_DEBUG_TOOLBAR")


ALLOWED_HOSTS = [
    'localhost',
]

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'


STATICFILES_DIRS = (
    str(ROOT_DIR / 'eruditorg' / 'static' / 'build_dev'),
    str(ROOT_DIR / 'eruditorg' / 'static' / 'build'),
    str(ROOT_DIR / 'eruditorg' / 'static'),
)


# no template caching when developping
TEMPLATES[0]['OPTIONS']['loaders'] = [
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
]

if ACTIVATE_DEBUG_TOOLBAR:
    INSTALLED_APPS += (
        'debug_toolbar',
        'debug_toolbar_line_profiler',
        'template_timings_panel',
        'eulfedora',
    )

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

    MIDDLEWARE += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )
