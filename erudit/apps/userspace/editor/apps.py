# -*- coding: utf-8 -*-

from django.apps import AppConfig


class EditorConfig(AppConfig):
    label = 'userspace_editor'
    name = 'apps.userspace.editor'

    def ready(self):
        from . import receivers  # noqa
