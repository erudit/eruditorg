from django.conf import settings


# Embargo year offsets


SCIENTIFIC_JOURNAL_EMBARGO_IN_MONTHS = getattr(settings, "SCIENTIFIC_JOURNAL_EMBARGO_IN_MONTHS", 12)

CULTURAL_JOURNAL_EMBARGO_IN_MONTHS = getattr(settings, "CULTURAL_JOURNAL_EMBARGO_IN_MONTHS", 36)

DEFAULT_PRODUCTION_DELAY_IN_MONTHS = getattr(settings, "DEFAULT_PRODUCTION_DELAY_IN_MONTHS", 1)

DEFAULT_JOURNAL_EMBARGO_IN_MONTHS = getattr(settings, "DEFAULT_JOURNAL_EMBARGO_IN_MONTHS", 1)

# Fedora credentials
FEDORA_ROOT = (
    getattr(settings, "ERUDIT_FEDORA_ROOT", None)
    or getattr(settings, "FEDORA_ROOT", None)
    or "http://localhost:8080/fedora/"
)
FEDORA_USER = (
    getattr(settings, "ERUDIT_FEDORA_USER", None)
    or getattr(settings, "FEDORA_USER", None)
    or "fedoraAdmin"
)
FEDORA_PASSWORD = (
    getattr(settings, "ERUDIT_FEDORA_PASSWORD", None)
    or getattr(settings, "FEDORA_PASSWORD", None)
    or "fedoraAdmin"
)

FEDORA_PIDSPACE = getattr(settings, "ERUDIT_FEDORA_PIDSPACE", "erudit")
FEDORA_FILEBASED_CACHE_NAME = getattr(settings, "ERUDIT_FEDORA_FILEBASED_CACHE_NAME", "files")


# The JOURNAL_PROVIDERS setting defines the sets from which the journals can be retrieved using the
# import commands.
DEFAULT_JOURNAL_PROVIDERS = {
    "fedora": [
        {
            "collection_title": "Érudit",
            "collection_code": "erudit",
            "localidentifier": "erudit",
        },
    ],
}
JOURNAL_PROVIDERS = getattr(settings, "ERUDIT_JOURNAL_PROVIDERS", DEFAULT_JOURNAL_PROVIDERS)


# The THESIS_PROVIDERS setting defines the sets from which the thesis can be retrieved using the
# import commands.
DEFAULT_THESIS_PROVIDERS = {
    "oai": [],
}
THESIS_PROVIDERS = getattr(settings, "ERUDIT_THESIS_PROVIDERS", DEFAULT_THESIS_PROVIDERS)
