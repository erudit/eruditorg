# -*- coding: utf-8 -*-

from django.conf import settings
from django.utils.functional import cached_property
from eulfedora.util import RequestFailed
from requests.exceptions import ConnectionError

from .repository import api


class FedoraMixin(object):
    """
    The FedoraMixin defines a common way to associate Django models and its
    instances to eulfedora's models and Erudit's objects'
    """
    def get_full_identifier(self):
        """
        Returns the full identifier of the considered object. By default the FedoraMixin
        assumes that this identifier can be accessed through a ``localidentifier`` model
        field. But it can be computed from parent objects in order to get identifiers of
        the form: nb1.nb2.
        """
        return self.localidentifier

    @property
    def pid(self):
        return self.get_full_identifier()

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
        try:
            xml_content = self.fedora_object.xml_content
            return self.erudit_class(xml_content) if xml_content else None
        except (RequestFailed, ConnectionError):  # pragma: no cover
            if settings.DEBUG:
                # In DEBUG mode RequestFailed or ConnectionError errors can occur
                # really often because the dataset provided by the Fedora repository
                # is not complete.
                return
            raise

    @cached_property
    def erudit_object(self):
        return self.get_erudit_object()
