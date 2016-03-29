# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured

from .action_base import AccountActionBase
from .core.loading import load
from .exceptions import ActionAlreadyRegistered


class AccountActionPool(object):
    """
    Actions that can be tokenized are registered with the ActionPool using the register() method.
    It makes them available to the global actions system.
    """
    def __init__(self):
        self._registry = {}
        self.discovered = False

    def discover(self):
        """
        Discovers all the 'account_actions' Python modules that can be defined inside each Django
        application listed in INSTALLED_APPS. Discovering these modules is necessary to force the
        registration of AccountActionBase subclasses.
        """
        if self.discovered:
            return
        self.discovered = True
        load('account_actions')

    def register(self, action_class):
        """
        Registers the given action in order to configure the way it behaves when action tokens are
        created or consumed.
        """
        if action_class is not None and not issubclass(action_class, AccountActionBase):
            raise ImproperlyConfigured(
                'The \'action_class\' class must be a subclass of AccountActionBase, '
                '{!r} is not'.format(action_class))

        # An action can't be registered twice
        if action_class.name in self._registry.keys():
            raise ActionAlreadyRegistered(
                'Cannot register {!r}, this action is already registered'.format(action_class))

        action = action_class()
        self._registry[action_class.name] = action

    def unregister_all(self):
        """
        Unregister all the actions.
        """
        self._registry = {}

    def get_action(self, action_name):
        """
        Returns the instance associated with the given action name.
        """
        return self._registry.get(action_name, None)

    def get_actions(self):
        """
        Returns all the registered actions.
        """
        self.discover()
        return self._registry.values()


actions = AccountActionPool()
