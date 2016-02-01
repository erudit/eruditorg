# -*- coding: utf-8 -*-

from django.utils.functional import cached_property

from .conf import settings
from .repository import api


class FedoraMixin(object):
    """
    The FedoraMixin defines a common way to associate Django models and its
    instances to eulfedora's models and Erudit's objects'
    """
    def get_pid(self):
        pid = self.localidentifier
        return settings.PID_PREFIX + pid if pid else None

    @property
    def pid(self):
        return self.get_pid()

    def get_fedora_model(self):
        """
        Returns the eulfedora's model associated with the considered Django model.
        """
        raise NotImplementedError

    @property
    def fedora_model(self):
        return self.get_fedora_model()

    def get_fedora_object(self):
        """
        Returns the eulfedora's object associated with the considered Django object.
        """
        return self.fedora_model(api, self.pid)

    @cached_property
    def fedora_object(self):
        return self.get_fedora_object()

    def get_erudit_class(self):
        """
        Returns the liberuditarticle's class associated with the considered Django model.
        """
        raise NotImplementedError

    @property
    def erudit_class(self):
        return self.get_erudit_class()

    def get_erudit_object(self):
        """
        Returns the liberuditarticle's object associated with the considered Django object.
        """
        # TODO: this should be updated when the work on liberuditarticle is done.
        return self.erudit_class()

    @property
    def erudit_object(self):
        return self.get_erudit_object()
