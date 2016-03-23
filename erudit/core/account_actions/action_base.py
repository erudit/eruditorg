# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import inspect

from django.core.exceptions import ImproperlyConfigured
import six

from .core.compat import with_metaclass


class AccountActionMetaclass(type):
    """
    Ensures the AccountActionBase subclasses have the required values and proceed to some
    validations.
    """
    def __new__(cls, name, bases, attrs):
        super_new = super(AccountActionMetaclass, cls).__new__
        parents = [base for base in bases if isinstance(base, AccountActionMetaclass)]
        if not parents:
            # We stop here if we are considering AccountActionBase and not
            # one of its subclasses
            return super_new(cls, name, bases, attrs)
        new_action = super_new(cls, name, bases, attrs)

        # Performs some checks

        action_name = getattr(new_action, 'name', None)
        if action_name is None or not isinstance(action_name, six.string_types):
            raise ImproperlyConfigured('The "name" attribute must be a string')

        execute_method = getattr(new_action, 'execute', None)
        if execute_method is None or not inspect.isfunction(execute_method):
            raise ImproperlyConfigured('The "execute" method must be configured')

        return new_action


class AccountActionBase(with_metaclass(AccountActionMetaclass, object)):
    # The action must have a name!
    name = None

    # The action must define an "execute" method that will be called when an action token is
    # consumed. This method takes the AccountActionToken instance as argument.
    #
    # def execute(self, token):
    #     # Do something
    #     pass
    #

    # Optional attributes
    title = None

    def send_notification_email(self, token):
        """
        A single method whose aim is to send a email to notify the creation of an action token.
        It should be overridden on any subclass which have to send an email after the creation of
        an action token.
        """
        return
