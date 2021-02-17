from .client import EruditCacheClient


def cache_set(cache, key, value, timeout, pids=None):
    # Pass `pids` to our cache client only if we are using EruditCacheClient.
    if hasattr(cache, 'client') and isinstance(cache.client, EruditCacheClient):
        cache.client.set(key, value, timeout, pids=pids)
    else:
        cache.set(key, value, timeout)
