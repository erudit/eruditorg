import environ
import logging
import structlog
from pathlib import Path

from sentry_sdk.integrations.logging import LoggingIntegration
from structlog.stdlib import LoggerFactory

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration


BASE_DIR = Path(__file__).parent
ROOT_DIR = BASE_DIR.parents[2]

env = environ.Env(
    DEBUG=(bool, False),
    ACTIVATE_DEBUG_TOOLBAR=(bool, False),
    EXPOSE_OPENMETRICS=(bool, False),
    SENTRY_ENVIRONMENT=(str, "default"),
    SECRET_KEY=(str, None),
    ADMIN_URL=(str, "admin/"),
    ALLOWED_HOSTS=(list, []),
    USE_DOCKER=(str, "no"),
    INTERNAL_IPS=(list, ["127.0.0.1"]),
    STATIC_ROOT=(str, str(ROOT_DIR / "static")),
    MEDIA_ROOT=(str, str(ROOT_DIR / "media")),
    STATIC_URL=(str, "/static/"),
    FEDORA_ASSETS_EXTERNAL_URL=(str, None),
    MEDIA_URL=(str, "/media/"),
    UPLOAD_ROOT=(str, str(ROOT_DIR / "media" / "uploads")),
    MANAGED_COLLECTIONS=(list, ["erudit", "unb"]),
    MAIN_DATABASE_URL=(str, "mysql://root@localhost/eruditorg"),
    RESTRICTION_DATABASE_URL=(str, "mysql://root@localhost/restriction"),
    CACHE_URL=(str, "locmemcache://"),
    FEDORA_CACHE_TIMEOUT=(int, 60 * 60 * 24 * 30),
    EMAIL_HOST=(str, None),
    EMAIL_PORT=(int, 25),
    EMAIL_HOST_USER=(str, None),
    EMAIL_HOST_PASSWORD=(str, None),
    MAILCHIMP_UUID=(str, None),
    MAILCHIMP_ACTION_URL=(str, None),
    DEFAULT_FROM_EMAIL=(str, "info@erudit.org"),
    DEBUG_EMAIL_ADDRESS=(str, "info@erudit.org"),
    FEDORA_ROOT=(str, None),
    FEDORA_USER=(str, None),
    FEDORA_PASSWORD=(str, None),
    SOLR_ROOT=(str, None),
    VICTOR_SOAP_URL=(str, None),
    VICTOR_SOAP_USERNAME=(str, None),
    VICTOR_SOAP_PASSWORD=(str, None),
    ABONNEMENTS_BASKETS_BACKEND_URL=(str, None),
    KBART_2014_BACKEND_URL=(str, None),
    Z3950_HOST=(str, None),
    Z3950_PORT=(int, None),
    Z3950_DATABASE=(str, None),
    SUSHI_URL=(str, None),
    ERUDIT_COUNTER_BACKEND_URL=(str, None),
    SUBSCRIPTION_EXPORTS_ROOT=(str, None),
    BOOKS_DIRECTORY=(str, None),
    RESTRICTION_ABONNE_ICONS_PATH=(str, None),
    SCIENTIFIC_JOURNAL_EMBARGO_IN_MONTHS=(int, 12),
    CULTURAL_JOURNAL_EMBARGO_IN_MONTHS=(int, 36),
    DJANGO_LOG_DIRECTORY=(str, None),
    RAVEN_DSN=(str, None),
    FIXTURE_ROOT=(str, None),
    JOURNAL_FIXTURES=(str, None),
    ANALYTICS_HOTJAR_TRACKING_CODE=(str, None),
    ANALYTICS_GOOGLE_TRACKING_CODE=(str, None),
    GOOGLE_CASA_KEY=(str, None),
    REDIS_HOST=(str, None),
    REDIS_PORT=(int, None),
    REDIS_INDEX=(int, None),
    ELASTICSEARCH_STATS_INDEX=(str, "site_usage_20*"),
    ELASTICSEARCH_STATS_HOST=(str, None),
    ELASTICSEARCH_STATS_PORT=(str, "9200"),
    SESSION_ENGINE=(str, "django.contrib.sessions.backends.db"),
    POST_OFFICE=(
        {
            "cast": {
                "BATCH_SIZE": int,
                "OVERRIDE_RECIPIENTS": list,
            },
        },
        {"BATCH_SIZE": 25},
    ),
    WEBPACK_DEV_SERVER_URL=(str, ""),
    BOOKS_UPDATE_EMAILS=(list, []),
    CSRF_FAILURE_VIEW=(str, "apps.public.views.forbidden_view"),
    COUNTER_R5_FIRST_AVAILABLE_MONTH=(str, "2017-05-01"),
    COUNTER_R5_AVAILABLE_AFTER=(int, 28),
)
environ.Env.read_env(str(ROOT_DIR / ".env"))

# General configuration
# -----------------------------------------------------------------------------

ALLOWED_HOSTS = env("ALLOWED_HOSTS")
INTERNAL_IPS = env("INTERNAL_IPS")

if env("USE_DOCKER") == "yes":
    import socket

    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS += [ip[:-1] + "1" for ip in ips]

DEBUG = env("DEBUG")
SECRET_KEY = env("SECRET_KEY")
ADMIN_URL = env("ADMIN_URL")
MANAGED_COLLECTIONS = env("MANAGED_COLLECTIONS")

# Static and media files
# -----------------------------------------------------------------------------

STATIC_ROOT = env("STATIC_ROOT")
MEDIA_ROOT = env("MEDIA_ROOT")
UPLOAD_ROOT = env("UPLOAD_ROOT")
STATIC_URL = env("STATIC_URL")
MEDIA_URL = env("MEDIA_URL")
FEDORA_ASSETS_EXTERNAL_URL = env("FEDORA_ASSETS_EXTERNAL_URL")

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

STATICFILES_DIRS = (
    str(ROOT_DIR / "eruditorg" / "static" / "build"),
    str(ROOT_DIR / "eruditorg" / "static"),
)

# Initialize sentry
# -----------------------------------------------------------------------------


RAVEN_DSN = env("RAVEN_DSN")
if RAVEN_DSN:
    sentry_logging = LoggingIntegration(
        level=logging.INFO,  # Capture info and above as breadcrumbs
        event_level=logging.ERROR,  # Send errors as events
    )
    sentry_sdk.init(
        dsn=RAVEN_DSN,
        integrations=[sentry_logging, DjangoIntegration()],
        environment=env("SENTRY_ENVIRONMENT"),
    )


# Application definition
# -----------------------------------------------------------------------------

EXPOSE_OPENMETRICS = env("EXPOSE_OPENMETRICS")

INSTALLED_APPS = (
    # Érudit apps
    "base",
    "erudit",
    "apps.public.book",
    "apps.public.campaign",
    "apps.public.citations",
    "apps.public.journal",
    "apps.public.search",
    "apps.public.site_messages",
    "apps.public.thesis",
    "apps.userspace",
    "apps.userspace.journal",
    "apps.userspace.journal.authorization",
    "apps.userspace.journal.editor",
    "apps.userspace.journal.information",
    "apps.userspace.journal.subscription",
    "apps.userspace.library",
    "apps.userspace.library.authorization",
    "apps.userspace.library.members",
    "apps.userspace.library.stats",
    "apps.userspace.library.subscription_ips",
    "core.authorization",
    "core.accounts",
    "core.citations",
    "core.editor",
    "core.journal",
    "core.metrics",
    "core.subscription",
    "erudit.cache",
    # Third-party apps
    "modeltranslation",
    "polymorphic",
    "post_office",
    "taggit",
    # Django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.humanize",
    "django.contrib.sessions",
    "django.contrib.sitemaps",
    "django.contrib.messages",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    # Third-party apps
    "eruditarticle",
    "waffle",
    "account_actions",
    "resumable_uploads",
    "rules",
    "ckeditor",
    "django_fsm",
    "easy_pjax",
    "django_js_reverse",
    "widget_tweaks",
    "rangefilter",
    "adv_cache_tag",
    "reversion",
    "reversion_compare",
)

ADD_REVERSION_ADMIN = True

if EXPOSE_OPENMETRICS:
    INSTALLED_APPS = INSTALLED_APPS + ("django_prometheus",)

MIDDLEWARE = (
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.contrib.sites.middleware.CurrentSiteMiddleware",
    "base.middleware.LanguageCookieMiddleware",
    "core.subscription.middleware.SubscriptionMiddleware",
    "core.citations.middleware.SavedCitationListMiddleware",
    "waffle.middleware.WaffleMiddleware",
    "base.middleware.LogHttp404Middleware",
    "base.middleware.PolyglotLocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
)

if EXPOSE_OPENMETRICS:
    MIDDLEWARE = (
        ("django_prometheus.middleware.PrometheusBeforeMiddleware",)
        + MIDDLEWARE
        + ("django_prometheus.middleware.PrometheusAfterMiddleware",)
    )

ROOT_URLCONF = "base.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            str(ROOT_DIR / "eruditorg" / "templates"),
        ],
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.static",
                "django.template.context_processors.media",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "base.context_processors.cache_constants",
                "base.context_processors.common_settings",
                "apps.public.site_messages.context_processors.active_site_messages",
            ],
            "loaders": [
                (
                    "django.template.loaders.cached.Loader",
                    [
                        "django.template.loaders.filesystem.Loader",
                        "django.template.loaders.app_directories.Loader",
                    ],
                ),
            ],
            "builtins": [
                "easy_pjax.templatetags.pjax_tags",
            ],
        },
    },
]

LOGIN_URL = "public:auth:login"
LOGIN_REDIRECT_URL = "public:home"


# Databases
# -----------------------------------------------------------------------------

DATABASES = {
    "default": env.db("MAIN_DATABASE_URL"),
    "restriction": env.db("RESTRICTION_DATABASE_URL"),
}

DATABASE_ROUTERS = [
    "core.subscription.restriction.router.RestrictionRouter",
]


# Cache
# -----------------------------------------------------------------------------

CACHES = {
    "default": env.cache("CACHE_URL"),
    "files": env.cache("CACHE_URL"),
}
NEVER_TTL = 0  # Do not cache
SHORT_TTL = 60 * 60  # Cache for 1 hour
LONG_TTL = 60 * 60 * 24  # Cache for 1 day

# django-adv-cache-tag settings
# -----------------------------------------------------------------------------
# The first argument of the cache tag (after the fragment's name) will be used
# as a primary key in the cache key.
ADV_CACHE_INCLUDE_PK = True
# The last argument of the cache tag will be used as the cache version in the
# cache content (not the key). This means that the cache key will not change,
# but the cache content will be invalidated if the version change.
ADV_CACHE_VERSIONING = True
# Compress the cache content with zlib.
ADV_CACHE_COMPRESS = True

FEDORA_CACHE_TIMEOUT = env("FEDORA_CACHE_TIMEOUT")

# Emails
# -----------------------------------------------------------------------------
EMAIL_BACKEND = "post_office.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = env("EMAIL_PORT")
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
BOOKS_UPDATE_EMAILS = env("BOOKS_UPDATE_EMAILS")

# Addresses
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")
DEBUG_EMAIL_ADDRESS = env("DEBUG_EMAIL_ADDRESS")

TECH_EMAIL = "tech@erudit.org"
PUBLISHER_EMAIL = "edition@erudit.org"
COMMUNICATION_EMAIL = "media@erudit.org"
SUBSCRIPTION_EMAIL = "client@erudit.org"
ACCOUNT_EMAIL = "comptes@erudit.org"

# Internationalisation
# -----------------------------------------------------------------------------

LANGUAGE_CODE = "fr"

LANGUAGES = (
    ("fr", "Français"),
    ("en", "English"),
)

TIME_ZONE = "America/Toronto"

USE_I18N = True
USE_L10N = True

LOCALE_PATHS = (str(ROOT_DIR / "locale"),)

USE_TZ = True

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    "rules.permissions.ObjectPermissionBackend",
    "core.accounts.backends.EmailBackend",
]

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.BCryptPasswordHasher",
    "django.contrib.auth.hashers.SHA1PasswordHasher",
    "django.contrib.auth.hashers.MD5PasswordHasher",
    "django.contrib.auth.hashers.CryptPasswordHasher",
]

# External systems
# -----------------------------------------------------------------------------

# Fedora settings
FEDORA_ROOT = env("FEDORA_ROOT")
FEDORA_USER = env("FEDORA_USER")
FEDORA_PASSWORD = env("FEDORA_PASSWORD")

# Solr settings
SOLR_ROOT = env("SOLR_ROOT")
SOLR_TIMEOUT = 10

# Victor settings
VICTOR_SOAP_URL = env("VICTOR_SOAP_URL")
VICTOR_SOAP_USERNAME = env("VICTOR_SOAP_USERNAME")
VICTOR_SOAP_PASSWORD = env("VICTOR_SOAP_PASSWORD")

# KBART
ABONNEMENTS_BASKETS_BACKEND_URL = env("ABONNEMENTS_BASKETS_BACKEND_URL")
KBART_2014_BACKEND_URL = env("KBART_2014_BACKEND_URL")

# Journal providers
ERUDIT_JOURNAL_PROVIDERS = {
    "fedora": [
        {
            "collection_title": "Érudit",
            "collection_code": "erudit",
            "localidentifier": "erudit",
        },
        {
            "collection_title": "The Electronic Text Centre at UNB Libraries",
            "collection_code": "unb",
            "localidentifier": "unb",
        },
    ],
    "oai": [
        {
            "collection_title": "Persée",
            "collection_code": "persee",
            "endpoint": "http://oai.persee.fr/oai",
            "issue_metadataprefix": "persee_mets",
        },
    ],
}

SUSHI_URL = env("SUSHI_URL")
Z3950_HOST = env("Z3950_HOST")
Z3950_PORT = env("Z3950_PORT")
Z3950_DATABASE = env("Z3950_DATABASE")

ERUDIT_COUNTER_BACKEND_URL = env("ERUDIT_COUNTER_BACKEND_URL")


# Metrics and analytics
# -----------------------------------------------------------------------------
METRICS_ACTIVATED = False
# METRICS_INFLUXDB_HOST = env("METRICS_INFLUXDB_HOST", default='localhost')
# METRICS_INFLUXDB_PORT = env("METRICS_INFLUXDB_PORT", default=0)
# METRICS_INFLUXDB_DBNAME = env("METRICS_INFLUXDB_DBNAME", default="db")
# METRICS_INFLUXDB_USER = env("METRICS_INFLUXDB_USER", default="db")
# METRICS_INFLUXDB_PASSWORD = env("METRICS_INFLUXDB_PASSWORD", default="password")

# Paths
# -----------------------------------------------------------------------------

SUBSCRIPTION_EXPORTS_ROOT = env("SUBSCRIPTION_EXPORTS_ROOT")
BOOKS_DIRECTORY = env("BOOKS_DIRECTORY")

# Logging settings
# -----------------------------------------------------------------------------

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "root": {
        "level": "INFO",
        "handlers": ["console"],
    },
    "handlers": {
        "referer": {
            "level": "DEBUG",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "when": "midnight",
            "filename": "/tmp/www.erudit.org.referer.log",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "root": {
            "level": "WARNING",
            "handlers": ["console"],
        },
        "core.subscription.middleware": {
            "level": "INFO",
            "handlers": [
                "referer",
                "console",
            ],
            "propagate": False,
        },
    },
}

structlog.configure(
    logger_factory=LoggerFactory(),
    processors=[
        structlog.dev.ConsoleRenderer(),
    ],
)

# MailChimp settings
# -----------------------------------

MAILCHIMP_UUID = env("MAILCHIMP_UUID", default=None)
MAILCHIMP_ACTION_URL = env("MAILCHIMP_ACTION_URL", default=None)

# Embargo
# -----------------------------------------------------------------------------

SCIENTIFIC_JOURNAL_EMBARGO_IN_MONTHS = env("SCIENTIFIC_JOURNAL_EMBARGO_IN_MONTHS")
CULTURAL_JOURNAL_EMBARGO_IN_MONTHS = env("CULTURAL_JOURNAL_EMBARGO_IN_MONTHS")

# Django JS reverse settings
# -----------------------------------

JS_REVERSE_INCLUDE_ONLY_NAMESPACES = [
    "public:citations",
    "public:search",
]

# Django-ckeditor settings
# -----------------------------------

CKEDITOR_CONFIGS = {
    "default": {
        "toolbar": "Custom",
        "toolbar_Custom": [
            ["Format", "Bold", "Italic", "Underline"],
            [
                "Image",
                "NumberedList",
                "BulletedList",
                "-",
                "JustifyLeft",
                "JustifyCenter",
                "JustifyRight",
                "JustifyBlock",
            ],
            ["Link", "Unlink"],
            ["RemoveFormat"],
        ],
    }
}

# Google CASA
# -----------
GOOGLE_CASA_KEY = env("GOOGLE_CASA_KEY")

# Redis
# -----
REDIS_HOST = env("REDIS_HOST")
REDIS_PORT = env("REDIS_PORT")
REDIS_INDEX = env("REDIS_INDEX")


# Elasticsearch (stats)
ELASTICSEARCH_STATS_INDEX = env("ELASTICSEARCH_STATS_INDEX")
ELASTICSEARCH_STATS_HOST = env("ELASTICSEARCH_STATS_HOST")
ELASTICSEARCH_STATS_PORT = env("ELASTICSEARCH_STATS_PORT")
# number of days after which last month's data is available as a counter R5 report
COUNTER_R5_AVAILABLE_AFTER = env("COUNTER_R5_AVAILABLE_AFTER")
# First month for which counter R5 data is available
COUNTER_R5_FIRST_AVAILABLE_MONTH = env("COUNTER_R5_FIRST_AVAILABLE_MONTH")

SESSION_ENGINE = env("SESSION_ENGINE")

# Help for lazyloading issue coverpages.
ISSUE_COVERPAGE_AVERAGE_SIZE = {
    "width": 135,
    "height": 200,
}

# Post Office
POST_OFFICE = env("POST_OFFICE")

WEBPACK_DEV_SERVER_URL = env("WEBPACK_DEV_SERVER_URL")

ACTIVATE_DEBUG_TOOLBAR = env("ACTIVATE_DEBUG_TOOLBAR")
