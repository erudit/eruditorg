# -*- coding: utf-8 -*-

from django.apps import AppConfig


class AccountActionsConfig(AppConfig):
    label = 'account_actions'
    name = 'core.account_actions'

    def ready(self):
        from . import receivers  # noqa
        from .action_pool import actions
        actions.discover()
