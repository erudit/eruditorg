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
        localidentifiers=[],
    ):
        redis = get_redis_connection()
        # Pass `localidentifiers` to our cache client only if we are using RedisKeyTagging.
        if isinstance(redis, RedisKeyTagging) and localidentifiers:
            return redis.set(
                self.make_key(key, version=version),
                self.encode(value),
                ex=timeout,
                tags=localidentifiers,
            )
        else:
            return super().set(key, value, timeout, version, client, nx, xx)
