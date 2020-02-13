# -*- coding: utf-8 -*-

import random

from django.core.cache import caches, cache
from django.utils.translation import get_language

from .serializers import get_datastream_cache_serializer
from ..conf import settings as erudit_settings


def cache_fedora_result(method, duration=erudit_settings.FEDORA_FILEBASED_CACHE_DEFAULT_TIMEOUT):
    """ Cache the result of a method called on a FedoraMixin object

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
            lang=get_language(),
            localidentifier=self.localidentifier,
            method_name=method.__name__
        )

        val = cache.get(key)

        if not val:
            duration_deviation = random.randint(-(duration // 4), duration // 4)
            val = method(self, *args, **kwargs)
            cache.set(key, val, duration + duration_deviation)
        return val
    return wrapper


def get_datastream_file_cache():
    return caches[erudit_settings.FEDORA_FILEBASED_CACHE_NAME]


def get_cached_datastream_content(fedora_object, datastream_name, cache=None):
    """ Given a Fedora object and a datastream name, returns the content of the datastream.

    Note that this content can be cached in a file-based cache!
    """
    cache = cache or get_datastream_file_cache()
    serializer, deserializer = get_datastream_cache_serializer(datastream_name)
    content_key = 'erudit-fedora-file-{pid}-{datastream_name}'.format(
        pid=fedora_object.pid,
        datastream_name=datastream_name,
    )

    content = deserializer(cache.get(content_key))
    try:
        assert content is None
        content = getattr(fedora_object, datastream_name).content
    except AssertionError:
        # We've just retrieved the content of the file from the file-based cache!
        pass
    else:
        # Puts the content of the file in the file-based cache!
        cache.set(
            content_key,
            serializer(content),
            erudit_settings.FEDORA_FILEBASED_CACHE_DEFAULT_TIMEOUT
        )

    return content
