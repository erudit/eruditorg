from adv_cache_tag.tag import CacheTag
from django import template

from ..client import EruditCacheClient


class EruditCacheTag(CacheTag):
    def cache_set(self, to_cache):
        # Pass `pids` to our cache client only if we are using EruditCacheClient.
        if hasattr(self.cache, "client") and isinstance(self.cache.client, EruditCacheClient):
            self.cache.client.set(
                self.cache_key,
                to_cache,
                timeout=self.expire_time,
                pids=self.context.get("cache_pids", []),
            )
        else:
            super().cache_set(to_cache)


register = template.Library()
EruditCacheTag.register(register, "cache")
