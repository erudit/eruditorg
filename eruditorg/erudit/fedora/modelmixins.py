from typing import Optional
import io
import requests
import structlog

from django.conf import settings
from django.utils.functional import cached_property
from lxml import etree
from PIL import Image
from requests.exceptions import HTTPError, ConnectionError
from eruditarticle.objects import EruditBaseObject
from sentry_sdk import configure_scope

from .cache import get_cached_datastream_content

logger = structlog.getLogger(__name__)


class FedoraMixin:
    """
    The FedoraMixin defines a common way to associate Django models to its Erudit's object.
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

    def get_erudit_object_datastream_name(self):
        """Returns the name of the datastream that will
        be parsed to instanciate the EruditObject"""
        raise NotImplementedError

    def get_erudit_class(self):
        """
        Returns the liberuditarticle's class associated with the considered Django model.
        """
        raise NotImplementedError

    @property
    def erudit_class(self):
        return self.get_erudit_class()

    def get_erudit_object(self) -> Optional[EruditBaseObject]:
        """
        Returns the liberuditarticle's object associated with the considered Django object.
        """
        fedora_xml_content = get_cached_datastream_content(
            self.pid,
            self.get_erudit_object_datastream_name(),
            cache_key=self.localidentifier,
        )
        return self.erudit_class(fedora_xml_content) if fedora_xml_content else None

    @cached_property
    def is_in_fedora(self):
        """Checks if an objet is present in fedora

        The presence of a full_identifier is not sufficient to determine if the object
        is present in fedora. Some articles have Fedora ids but are _not_ in Fedora."""
        return bool(self.get_full_identifier() and self.erudit_object)

    @cached_property
    def erudit_object(self):
        if not self.fedora_is_loaded():
            self._erudit_object = self.get_erudit_object()
        return self._erudit_object

    def fedora_is_loaded(self):
        return hasattr(self, "_erudit_object") and self._erudit_object is not None

    def has_non_empty_image_datastream(self, datastream_name: str) -> bool:
        """Returns True if the considered fedora object has a non empty image datastream.

        Returns False tf the considered image datastream is not is Fedora.

        Returns False if the considered image datastream is in Fedora but is empty (one color only).

        To check if the image is empty (one color only), we convert it to greyscale and get the
        minimum and maximum pixel values. If the minimum and maximum pixel values are both white or
        both black, we consider the image as being empty.
        """
        content = get_cached_datastream_content(self.pid, datastream_name)
        if not content:
            return False

        # Checks the content of the image in order to detect if it contains only one single color.
        im = Image.open(io.BytesIO(content))
        # Convert the image to greyscale ("L") and get the minimum & maximum pixel values.
        extrema = im.convert("L").getextrema()
        # If the minimum & maximum pixel values are both white or both black, we consider the image
        # as being empty.
        empty_image = (extrema == (0, 0)) or (extrema == (255, 255))
        im.close()

        return not empty_image

    def has_datastream(self, datastream_name):
        """ Returns True if the considered fedora object has a given datastream. """
        try:
            response = requests.get(
                settings.FEDORA_ROOT + f"objects/{self.pid}/datastreams",
                {"format": "xml"},
            )
            response.raise_for_status()
            xml = etree.fromstring(response.content)
            datastream = xml.find(f"datastream[@dsid='{datastream_name}']", namespaces=xml.nsmap)
            return datastream is not None

        except HTTPError as e:
            # If the content is not found, return False.
            if e.response.status_code == 404:
                with configure_scope() as scope:
                    scope.fingerprint = ["fedora.warning"]
                    logger.warning("fedora.warning", message=str(e))
                return False

            # If there's a client error, raise a HTTPError.
            elif 400 <= e.response.status_code < 500:
                with configure_scope() as scope:
                    scope.fingerprint = ["fedora.client-error"]
                    logger.error("fedora.client-error", message=str(e))
                raise

            # If there's a server error, raise a HTTPError.
            elif 500 <= e.response.status_code < 600:
                with configure_scope() as scope:
                    scope.fingerprint = ["fedora.server-error"]
                    logger.error("fedora.server-error", message=str(e))
                raise

        except ConnectionError as e:
            # If Fedora is unreachable, raise a ConnectionError.
            with configure_scope() as scope:
                scope.fingerprint = ["fedora.connection-error"]
                logger.error("fedora.connection-error", message=str(e))
            raise
