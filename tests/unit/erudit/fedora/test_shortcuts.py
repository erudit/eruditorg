import unittest.mock

from erudit.fedora import repository
from erudit.fedora.cache import get_cached_datastream_content


def test_can_set_the_content_of_the_file_in_the_cache_if_it_is_not_there_already():
    repository.api.register_pid("erudit:erudit.foo123.bar456")
    repository.api.register_datastream(
        "erudit:erudit.foo123.bar456",
        "/SUMMARY/content",
        "dummy",
    )

    with unittest.mock.patch("erudit.fedora.cache.cache") as mock_cache:
        mock_cache.get.return_value = None
        get_cached_datastream_content("erudit:erudit.foo123.bar456", "SUMMARY")
        assert mock_cache.get.call_count == 1
        assert mock_cache.set.call_count == 1


def test_can_use_the_content_of_the_file_in_the_cache_if_applicable():
    repository.api.register_pid("erudit:erudit.foo123.bar456")
    repository.api.register_datastream(
        "erudit:erudit.foo123.bar456",
        "/SUMMARY/content",
        "dummy",
    )

    with unittest.mock.patch("erudit.fedora.cache.cache") as mock_cache:
        mock_cache.get.return_value = "dummy"
        get_cached_datastream_content("erudit:erudit.foo123.bar456", "SUMMARY")
        assert mock_cache.get.call_count == 1
        assert mock_cache.set.call_count == 0
