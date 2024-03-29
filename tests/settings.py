import logging
import os

from base.settings.base import *  # noqa

DEBUG = True


TEST_ROOT = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = "insecure"

CACHES = {
    "default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"},
    "files": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    },
}

# Not an actual setting, but can be used in some tests with @override_settings
LOCMEM_CACHES = {
    "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
    "files": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    },
}

DATABASES = {
    "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"},
}

DATABASE_ROUTERS = [
    "core.subscription.restriction.router.RestrictionRouter",
]

RESTRICTION_MODELS_ARE_MANAGED = True

MANAGED_COLLECTIONS = ("erudit",)

MEDIA_ROOT = os.path.join(TEST_ROOT, "_testdata/media/")
UPLOAD_ROOT = MEDIA_ROOT

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

INSTALLED_APPS = list(INSTALLED_APPS)
INSTALLED_APPS.append("core.subscription.restriction")
INSTALLED_APPS.append("tests")

MIGRATION_MODULES = {
    "auth": None,
    "authorization": None,
    "contenttypes": None,
    "sessions": None,
    "erudit": None,
    "accounts": None,
    "citations": None,
    "editor": None,
    "subscription": None,
    "taggit": None,
    "waffle": None,
    "account_actions": None,
    "resumable_uploads": None,
    "reversion": None,
}

USE_DEBUG_EMAIL = False

FEDORA_ROOT = "http://erudit.org/"
SOLR_ROOT = "http://erudit.org/"

POST_OFFICE = {
    "DEFAULT_PRIORITY": "now",
}

EDITOR_MAIN_PRODUCTION_TEAM_IDENTIFIER = "main-production-team"

BOOKS_UPDATE_EMAILS = ["foo@bar.com", "foo@baz.com"]

MIDDLEWARE = tuple(m for m in MIDDLEWARE if m != "whitenoise.middleware.WhiteNoiseMiddleware")

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

logging.disable(logging.CRITICAL)
