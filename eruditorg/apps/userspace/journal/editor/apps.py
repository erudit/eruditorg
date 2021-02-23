# -*- coding: utf-8 -*-

from django.apps import AppConfig


class EditorConfig(AppConfig):
    label = "userspace_journal_editor"
    name = "apps.userspace.journal.editor"

    def ready(self):
        from . import receivers  # noqa
