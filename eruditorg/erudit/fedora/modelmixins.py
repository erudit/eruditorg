import structlog

from django.conf import settings
from django.core.cache import caches
from django.utils.functional import cached_property

from sentry_sdk import configure_scope
from eulfedora.util import RequestFailed
from requests.exceptions import ConnectionError

from ..conf import settings as erudit_settings
from .repository import api

logger = structlog.getLogger(__name__)
cache = caches['default']


class FedoraMixin:
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

    def _should_use_cache(self):
        """ Tells FedoraMixin to use cache or not

        This method lets the child objects of ``FedoraMixin`` implement the rules by which
        ``FedoraMixin`` will determine if the cache should be used or not.

        :return: True if the cache should be used for the given object.
        """
        return True

    def get_fedora_object(self):
        """
        Returns the eulfedora's object associated with the considered Django object.
        """

        if not self.get_full_identifier():
            return None

        if not self._should_use_cache():
            return self.fedora_model(api, self.pid)

        if getattr(self, '_fedora_object', None) is None:
            self._fedora_object = self.fedora_model(api, self.pid)
        return self._fedora_object

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

    def get_erudit_object(self, fedora_object=None, use_cache=True):
        """
        Returns the liberuditarticle's object associated with the considered Django object.
        """

        if self._should_use_cache() and use_cache:
            fedora_xml_content_key = self.localidentifier
            fedora_xml_content = cache.get(fedora_xml_content_key, None)
        else:
            fedora_xml_content_key = None
            fedora_xml_content = None

        try:
            assert fedora_xml_content is None
            fedora_object = self.get_fedora_object()
            fedora_xml_content = fedora_object.xml_content
        except (RequestFailed, ConnectionError):  # pragma: no cover
            with configure_scope() as scope:
                scope.fingerprint = ['fedora-warnings']
                logger.warning("fedora.exception", pid=self.pid)

            if settings.DEBUG:
                # In DEBUG mode RequestFailed or ConnectionError errors can occur
                # really often because the dataset provided by the Fedora repository
                # is not complete.
                return
            elif hasattr(self, 'issue') and self.issue.journal.collection.code == 'unb':
                # The UNB collection *has* articles that are missing from Fedora
                return
            raise
        except AssertionError:
            # We've fetched the XML content from the cache so we just pass
            pass
        else:
            # Stores the XML content of the object for further use
            if self._should_use_cache() and use_cache:
                cache.set(
                    fedora_xml_content_key, fedora_xml_content,
                    self.fedora_xml_content_cache_timeout
                )

        return self.erudit_class(fedora_xml_content) if fedora_xml_content else None

    @cached_property
    def is_in_fedora(self):
        """ Checks if an objet is present in fedora

        The presence of a full_identifier is not sufficient to determine if the object
        is present in fedora. Some articles have Fedora ids but are _not_ in Fedora."""
        try:
            return self.get_full_identifier() and self.erudit_object
        except RequestFailed:
            return False

    @cached_property
    def erudit_object(self):
        if not self.fedora_is_loaded():
            self._erudit_object = self.get_erudit_object()
        return self._erudit_object

    def reset_fedora_objects(self):
        self._fedora_object = None
        self._erudit_object = None

    def fedora_is_loaded(self):
        return hasattr(self, '_erudit_object') and self._erudit_object is not None
