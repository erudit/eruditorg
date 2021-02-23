from django.apps import AppConfig


class BaseConfig(AppConfig):
    """
    Autodiscovering rules (from rules app) is triggred by this module because
    it failed form rules apps (navutils autodiscover throw an exception when
    it try to lookup in rules.apps.xxx)
    """

    name = "base"

    def ready(self):
        from django.utils.module_loading import autodiscover_modules

        autodiscover_modules("rules")
