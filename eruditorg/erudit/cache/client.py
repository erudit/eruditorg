from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django_redis import get_redis_connection
from django_redis.client import DefaultClient

from redis_key_tagging.client import RedisKeyTagging


class EruditCacheClient(DefaultClient):
    def set(
        self,
        key,
        value,
        timeout=DEFAULT_TIMEOUT,
        version=None,
        client=None,
        nx=False,
        xx=False,
        pids=[],
    ):
        redis = get_redis_connection()

        # Django's DEFAULT_TIMEOUT is an object() to force backends to set their own default timeout
        # values, so let's set our own default timeout here.
        if timeout == DEFAULT_TIMEOUT:
            timeout = settings.SHORT_TTL

        # Pass tags to our cache client only if we are using RedisKeyTagging, if we have a positive
        # or a `None` timeout, and if we have pids.
        if isinstance(redis, RedisKeyTagging) and (timeout is None or timeout > 0) and pids:
            return redis.set(
                self.make_key(key, version=version),
                self.encode(value),
                ex=timeout,
                tags=pids,
            )
        else:
            return super().set(key, value, timeout, version, client, nx, xx)
