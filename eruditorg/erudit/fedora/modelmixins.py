from typing import Optional, Type
import io
import structlog
import requests

from django.conf import settings
from django.utils.functional import cached_property
from lxml import etree
from PIL import Image
from eulfedora.util import RequestFailed
from requests.exceptions import HTTPError, ConnectionError
from eruditarticle.objects import EruditBaseObject

from .cache import get_cached_datastream_content
from .repository import api

logger = structlog.getLogger(__name__)


class FedoraMixin:
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

    def get_erudit_object_datastream_name(self):
        """Returns the name of the datastream that will
        be parsed to instanciate the EruditObject"""
        raise NotImplementedError

    def get_fedora_object(self):
        """
        Returns the eulfedora's object associated with the considered Django object.
        """

        if not self.get_full_identifier():
            return None

        if getattr(self, "_fedora_object", None) is None:
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

    def get_erudit_object(self) -> Optional[Type[EruditBaseObject]]:
        """
        Returns the liberuditarticle's object associated with the considered Django object.
        """
        try:
            fedora_xml_content = get_cached_datastream_content(
                self.pid,
                self.get_erudit_object_datastream_name(),
                cache_key=self.localidentifier,
            )
            if fedora_xml_content is None:
                raise HTTPError
            return self.erudit_class(fedora_xml_content)

        except (HTTPError, ConnectionError):  # pragma: no cover
            if settings.DEBUG:
                # In DEBUG mode RequestFailed or ConnectionError errors can occur
                # really often because the dataset provided by the Fedora repository
                # is not complete.
                return
            elif hasattr(self, "issue") and self.issue.journal.collection.code == "unb":
                # The UNB collection *has* articles that are missing from Fedora
                return
            raise

    @cached_property
    def is_in_fedora(self):
        """Checks if an objet is present in fedora

        The presence of a full_identifier is not sufficient to determine if the object
        is present in fedora. Some articles have Fedora ids but are _not_ in Fedora."""
        try:
            return bool(self.get_full_identifier() and self.erudit_object)
        except (HTTPError, ConnectionError):
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
        return hasattr(self, "_erudit_object") and self._erudit_object is not None

    def has_non_empty_image_datastream(self, datastream_name: str) -> bool:
        """ Returns True if the considered fedora object has a non empty image datastream. """
        if self.fedora_object is None:
            return False
        try:
            content = get_cached_datastream_content(self.pid, datastream_name)
        except RequestFailed:
            return False

        if not content:
            return False

        # Checks the content of the image in order to detect if it contains only one single color.
        im = Image.open(io.BytesIO(content))
        extrema = im.convert("L").getextrema()
        empty_image = (extrema == (0, 0)) or (extrema == (255, 255))
        im.close()

        return not empty_image

    def has_datastream(self, datastream_name):
        try:
            response = requests.get(
                settings.FEDORA_ROOT + f"objects/{self.pid}/datastreams",
                {"format": "xml"},
            )
            response.raise_for_status()
            xml = etree.fromstring(response.content)
            datastream = xml.find(f"datastream[@dsid='{datastream_name}']", namespaces=xml.nsmap)
            return datastream is not None
        except (HTTPError, ConnectionError):
            return False
