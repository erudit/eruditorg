# -*- coding: utf-8 -*-
import typing
import random
import requests
import structlog

from django.conf import settings
from django.core.cache import cache
from django.utils.translation import get_language
from requests.exceptions import HTTPError, ConnectionError
from sentry_sdk import configure_scope

from erudit.cache import cache_set

logger = structlog.getLogger(__name__)


def cache_fedora_result(method, duration=settings.LONG_TTL):
    """Cache the result of a method called on a FedoraMixin object

    Assumes that the method is bound to a FedoraMixin object, or at least that the object has a
    ``localidentifier`` attribute.

    If the value of ``localidentifier`` is ``None``, cache will not be queried and the decorated
    method will be called directly.

    This decorator assumes that the localidentifier is unique for ALL Fedora objects.

    Will cache the result for the value of ``duration``, plus or minus ``duration`` * 0.25. This
    is to avoid expiring all the cached resources at the same time.

    :param method: the method to decorate
    :param duration: expected duration of result cache
    :return: the decorated method
    """

    def wrapper(self, *args, **kwargs):

        if not self.localidentifier:
            return method(self, *args, **kwargs)

        key = "fedora_result-{lang}-{localidentifier}-{method_name}".format(
            lang=get_language(), localidentifier=self.localidentifier, method_name=method.__name__
        )

        val = cache.get(key)

        if not val:
            duration_deviation = random.randint(-(duration // 4), duration // 4)
            val = method(self, *args, **kwargs)
            cache_set(
                cache,
                key,
                val,
                duration + duration_deviation,
                pids=[self.pid],
            )
        return val

    return wrapper


def get_cached_datastream_content(
    pid: str, datastream_name: str, cache_key: typing.Optional[str] = None
) -> typing.Optional[bytes]:
    """
    Given an object pid and a datastream name, returns the content of the datastream.

    The content may be fetched from the cache, if it was previously cached, or directly from Fedora.

    If the content was not already cached, it will now be cached using the optional cache key
    argument, if provided, or with a unique generated a cache key using the object pid and the
    datastream name.

    If there is a client error (4xx HTTPError), this function will return None.

    If there is a server error (5xx HTTPError) or if there is a ConnectionError, this function
    will raise the exception.
    """
    content_key = f"erudit-fedora-file-{pid}-{datastream_name}" if not cache_key else cache_key
    content = cache.get(content_key)

    # If content is already cached, return it.
    if content is not None:
        return content

    try:
        # Otherwise, get the content from Fedora and cache it for future use.
        response = requests.get(
            settings.FEDORA_ROOT + f"objects/{pid}/datastreams/{datastream_name}/content",
        )
        response.raise_for_status()
        content = response.content

        cache_set(
            cache,
            content_key,
            content,
            settings.FEDORA_CACHE_TIMEOUT,
            pids=[pid],
        )
        return content

    except HTTPError as e:
        # If there is a client error, return None.
        if 400 <= e.response.status_code < 500:
            with configure_scope() as scope:
                scope.fingerprint = ["fedora.warning"]
                logger.warning("fedora.warning", message=str(e))
            return None

        # If there is a server error, raise a HTTPError.
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
