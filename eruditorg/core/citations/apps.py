# -*- coding: utf-8 -*-

from django.apps import AppConfig


class CitationsAppConfig(AppConfig):
    label = "citations"
    name = "core.citations"

    def ready(self):
        from . import receivers  # noqa
