# -*- coding: utf-8 -*-

import logging

from django.conf import settings
from django.core.cache import cache
from django.utils.functional import cached_property
from eulfedora.util import RequestFailed
from requests.exceptions import ConnectionError

from ..conf import settings as erudit_settings
from .repository import api

logger = logging.getLogger(__name__)


class FedoraMixin(object):
    """
    The FedoraMixin defines a common way to associate Django models and its
    instances to eulfedora's models and Erudit's objects'
    """
    fedora_xml_content_cache_timeout = erudit_settings.FEDORA_XML_CONTENT_CACHE_TIMEOUT

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
        if self.get_full_identifier():
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
        fedora_xml_content_key = 'fedora-object-{pid}'.format(pid=self.pid)
        fedora_xml_content = cache.get(fedora_xml_content_key, None)

        try:
            assert fedora_xml_content is None
            fedora_xml_content = self.fedora_object.xml_content
        except (RequestFailed, ConnectionError) as e:  # pragma: no cover
            logger.warn("Exception: {}, pid: {}".format(e, self.pid))
            if settings.DEBUG:
                # In DEBUG mode RequestFailed or ConnectionError errors can occur
                # really often because the dataset provided by the Fedora repository
                # is not complete.
                return
            raise
        except AssertionError:
            # We've fetched the XML content from the cache so we just pass
            pass
        else:
            # Stores the XML content of the object for further use
            cache.set(
                fedora_xml_content_key, fedora_xml_content, self.fedora_xml_content_cache_timeout)

        return self.erudit_class(fedora_xml_content) if fedora_xml_content else None

    @cached_property
    def erudit_object(self):
        return self.get_erudit_object()
