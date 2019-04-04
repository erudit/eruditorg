"""
Django settings for erudit project.

Generated by 'django-admin startproject' using Django 1.8.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

from pathlib import Path
import structlog
from structlog.stdlib import LoggerFactory

from structlog.processors import JSONRenderer
from datetime import datetime

DEBUG = True
COMPRESS_ENABLED = True

BASE_DIR = Path(__file__)
ROOT_DIR = BASE_DIR.parents[3]

STATIC_ROOT = str(ROOT_DIR / 'static')
MEDIA_ROOT = str(ROOT_DIR / 'media')
UPLOAD_ROOT = str(ROOT_DIR / 'media' / 'uploads')

# destination path for https://gitlab.erudit.org/erudit/rapports/rapports_editeurs
SUBSCRIPTION_EXPORTS_ROOT = str(ROOT_DIR / 'rapports_editeurs')

# URL of the admin page
ADMIN_URL = 'admin/'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

SECRET_KEY = 'INSECURE'

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = (
    # Érudit apps
    'base',
    'erudit',
    'apps.public.book',
    'apps.public.citations',
    'apps.public.journal',
    'apps.public.search',
    'apps.public.site_messages',
    'apps.public.thesis',
    'apps.userspace',
    'apps.userspace.journal',
    'apps.userspace.journal.authorization',
    'apps.userspace.journal.editor',
    'apps.userspace.journal.information',
    'apps.userspace.journal.subscription',
    'apps.userspace.library',
    'apps.userspace.library.authorization',
    'apps.userspace.library.members',
    'apps.userspace.library.stats',
    'apps.userspace.library.subscription_ips',
    'apps.userspace.reporting',
    'core.authorization',
    'core.accounts',
    'core.citations',
    'core.editor',
    'core.journal',
    'core.metrics',
    'core.reporting',
    'core.subscription',

    # Third-party apps
    'modeltranslation',
    'polymorphic',
    'post_office',
    'taggit',

    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.sitemaps',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.staticfiles',

    # Third-party apps
    'eruditarticle',
    'waffle',
    'account_actions',
    'resumable_uploads',
    'rules',
    'ckeditor',
    'raven.contrib.django.raven_compat',
    'django_fsm',
    'easy_pjax',
    'django_js_reverse',
    'widget_tweaks',
    'rangefilter',
)

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

STATICFILES_DIRS = (
    str(ROOT_DIR / 'eruditorg' / 'static' / 'build'),
    str(ROOT_DIR / 'eruditorg' / 'static'),
)

MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'base.middleware.LanguageCookieMiddleware',
    'core.subscription.middleware.SubscriptionMiddleware',
    'core.citations.middleware.SavedCitationListMiddleware',
    'waffle.middleware.WaffleMiddleware',
    'base.middleware.RedirectToFallbackMiddleware',
    'base.middleware.PolyglotLocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
)

ROOT_URLCONF = 'base.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            str(ROOT_DIR / 'eruditorg' / 'templates'),
        ],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.template.context_processors.media',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'base.context_processors.cache_constants',
                'base.context_processors.common_settings',
                'apps.public.site_messages.context_processors.active_site_messages',
            ],
            'loaders': [
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ]),
            ],
            'builtins': [
                'easy_pjax.templatetags.pjax_tags',
            ],
        },
    },
]


LOGIN_URL = 'public:auth:login'
LOGIN_REDIRECT_URL = 'public:home'
# Database configuration

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'eruditorg',
        'USER': 'root',
        'PASSWORD': '',
    },

    'restriction': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'restriction',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': '',
    },

}

DATABASE_ROUTERS = [
    'core.subscription.restriction.router.RestrictionRouter',
]


# Cache configuration

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    'fedora': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    'files': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/erudit_filebased',
    },
}

POST_OFFICE = {
    'BATCH_SIZE': 25,
}

MANAGED_COLLECTIONS = tuple()

EMAIL_BACKEND = 'post_office.EmailBackend'
EMAIL_HOST = "mail"
EMAIL_PORT = '25'
RENEWAL_FROM_EMAIL = 'admin@localhost'

DEFAULT_FROM_EMAIL = 'ne-pas-repondre@erudit.org'
TECH_EMAIL = 'tech@erudit.org'
PUBLISHER_EMAIL = 'edition@erudit.org'
COMMUNICATION_EMAIL = 'media@erudit.org'
SUBSCRIPTION_EMAIL = 'client@erudit.org'

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'fr'

LANGUAGES = (
    ('fr', 'Français'),
    ('en', 'English'),
)

TIME_ZONE = 'America/Toronto'

USE_I18N = True
USE_L10N = True

LOCALE_PATHS = (
    str(ROOT_DIR / 'locale'),
)

USE_TZ = True

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    'rules.permissions.ObjectPermissionBackend',
    'core.accounts.backends.EmailBackend',
]

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
    'core.accounts.hashers.DrupalPasswordHasher',
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

INDIVIDUAL_SUBSCRIPTION_SALT = 'sample salt'

# External systems
# -----------------------------------------------------------------------------

# Classic website
FALLBACK_BASE_URL = 'http://retro.erudit.org/'

# Fedora settings
FEDORA_ROOT = 'http://10.1.1.33:8080/fedora'
FEDORA_USER = 'fcAdmin'
FEDORA_PASSWORD = 'fcAdmin'

# Solr settings
SOLR_ROOT = 'http://10.1.1.33:8080/solr/eruditpersee/'
SOLR_TIMEOUT = 10

# Books directory
BOOKS_DIRECTORY = None

# Victor settings
VICTOR_SOAP_URL = None
VICTOR_SOAP_USERNAME = None
VICTOR_SOAP_PASSWORD = None

# Logging settings

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {
        'level': 'INFO',
        'handlers': ['sentry', 'console'],
    },
    'formatters': {
        'structured': {
            'format': '%(message)s'
        },
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'sentry': {
            'level': 'WARNING',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
        'referer': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'midnight',
            'filename': '/tmp/www.erudit.org.referer.log',
            'formatter': 'verbose',
        },

        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'structured'
        },
    },
    'loggers': {
        'core.subscription.middleware': {
            'level': 'INFO',
            'handlers': ['referer', ],
            'propagate': False,
        },
    }
}


def add_timestamp(_, __, event_dict):
    event_dict['timestamp'] = datetime.utcnow().strftime("%x %X")
    return event_dict


structlog.configure(
    logger_factory=LoggerFactory(),
    processors=[
        add_timestamp,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.format_exc_info,
        JSONRenderer(sort_keys=True)
    ]
)


# Raven settings
RAVEN_CONFIG = {
    'dsn': None,
}

# Openmetrics
# -----------------------------------

EXPOSE_OPENMETRICS = False

# MailChimp settings
# -----------------------------------

MAILCHIMP_UUID = ""
MAILCHIMP_ACTION_URL = ""


# Django JS reverse settings
# -----------------------------------

JS_REVERSE_INCLUDE_ONLY_NAMESPACES = ['public:citations', 'public:search', ]

# Django-ckeditor settings
# -----------------------------------

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Format', 'Bold', 'Italic', 'Underline'],
            ['Image', 'NumberedList', 'BulletedList', '-', 'JustifyLeft',
             'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['Link', 'Unlink'],
            ['RemoveFormat']
        ]
    }
}


try:
    from .settings_env import *  # noqa
except ImportError:
    pass

try:
    from ..settings_env import *  # noqa
except ImportError:
    pass
