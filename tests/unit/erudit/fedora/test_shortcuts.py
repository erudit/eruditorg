import unittest.mock

from erudit.fedora import repository
from erudit.fedora.cache import get_cached_datastream_content


def test_can_set_the_content_of_the_file_in_the_cache_if_it_is_not_there_already():
    mock_fedora_obj = unittest.mock.MagicMock()
    mock_fedora_obj.dstream = unittest.mock.MagicMock()
    mock_fedora_obj.dstream.content = 'dummy'
    mock_fedora_obj.pid = 'erudit:erudit.foo123.bar456'
    repository.api.register_pid('erudit:erudit.foo123.bar456')
    repository.api.register_datastream(
        'erudit:erudit.foo123.bar456',
        '/SUMMARY/content',
        'dummy',
    )
    mock_cache = unittest.mock.MagicMock()
    mock_cache_get = unittest.mock.MagicMock()
    mock_cache_get.return_value = None
    mock_cache_set = unittest.mock.MagicMock()
    mock_cache.get = mock_cache_get
    mock_cache.set = mock_cache_set
    get_cached_datastream_content(mock_fedora_obj, 'SUMMARY', cache=mock_cache)
    assert mock_cache_get.call_count == 1
    assert mock_cache_set.call_count == 1


def test_can_use_the_content_of_the_file_in_the_cache_if_applicable():
    mock_fedora_obj = unittest.mock.MagicMock()
    mock_fedora_obj.dstream = unittest.mock.MagicMock()
    mock_fedora_obj.dstream.content = 'dummy'
    mock_fedora_obj.pid = 'erudit:erudit.foo123.bar456'
    repository.api.register_pid('erudit:erudit.foo123.bar456')
    repository.api.register_datastream(
        'erudit:erudit.foo123.bar456',
        '/SUMMARY/content',
        'dummy',
    )
    mock_cache = unittest.mock.MagicMock()
    mock_cache_get = unittest.mock.MagicMock()
    mock_cache_get.return_value = 'dummy'
    mock_cache_set = unittest.mock.MagicMock()
    mock_cache.get = mock_cache_get
    mock_cache.set = mock_cache_set
    get_cached_datastream_content(mock_fedora_obj, 'SUMMARY', cache=mock_cache)
    assert mock_cache_get.call_count == 1
    assert mock_cache_set.call_count == 0
