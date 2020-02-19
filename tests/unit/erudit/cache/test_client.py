import pytest

from redis_key_tagging.client import RedisKeyTagging
from unittest.mock import Mock, patch

from erudit.cache.client import EruditCacheClient


class MockRedisKeyTagging(RedisKeyTagging):
    def set(self, key, value, ex, tags):
        return "redis_key_tagging was used"


class TestEruditCacheClient:

    @pytest.mark.parametrize("redis", (Mock(), MockRedisKeyTagging()))
    @pytest.mark.parametrize("timeout", (0, 10, -1, None))
    @pytest.mark.parametrize("pids", ([], ["tag"]))
    @patch("erudit.cache.client.get_redis_connection")
    @patch("erudit.cache.client.EruditCacheClient.make_key")
    @patch("erudit.cache.client.EruditCacheClient.encode")
    @patch("erudit.cache.client.EruditCacheClient.__init__", return_value=None)
    @patch("erudit.cache.client.DefaultClient.set", return_value="django_redis was used")
    def test_set(
        self,
        mock_set,
        mock_init,
        mock_encode,
        mock_make_key,
        mock_get_redis_connection,
        redis,
        timeout,
        pids,
    ):
        mock_get_redis_connection.return_value = redis
        cache = EruditCacheClient()
        result = cache.set("key", "value", timeout, pids=pids)
        # Only use redis_key_tagging if our Redis connection is a RedisKeyTagging instance, if we
        # have a positive or a `None` timeout, and if we have pids. Otherwise, use django_redis.
        if isinstance(redis, RedisKeyTagging) and (timeout is None or timeout > 0) and pids:
            assert result == "redis_key_tagging was used"
        else:
            assert result == "django_redis was used"
