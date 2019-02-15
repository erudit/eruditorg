# -*- coding: utf-8 -*-

from django.apps import AppConfig

EMAIL_TAG = "www-depot-fichier"


class EditorConfig(AppConfig):
    label = 'editor'
    name = 'core.editor'

    def ready(self):
        from . import receivers  # noqa
