import pytest

from base.middleware import PolyglotLocaleMiddleware
from django.test import RequestFactory
from django.http.response import HttpResponse
from django.utils import translation
from unittest import mock


@pytest.mark.django_db
class TestPolyglotLocaleMiddleware:

    @pytest.mark.parametrize('src_url, dest_url', [
        ('/revues/', '/en/journals/'),
        ('/revues', '/en/journals/'),
        ('/journals', '/en/journals/')
    ])
    def test_can_resolve_different_language_url_when_no_language_code_is_specified(self, src_url, dest_url):
        middleware = PolyglotLocaleMiddleware()
        translation.activate("en")
        request = RequestFactory().get(src_url)

        response = mock.MagicMock(HttpResponse, autospec=True)
        response.status_code = 404
        response.has_header.return_value = False
        response = middleware.process_response(request, response)
        assert response.status_code == 302
        assert response.url == dest_url

    @pytest.mark.parametrize('language',
        ('fr', 'en')
    )
    def test_middleware_leaves_active_language_intact(self, language):
        middleware = PolyglotLocaleMiddleware()
        translation.activate(language)
        request = RequestFactory().get("/journals")

        response = mock.MagicMock(HttpResponse, autospec=True)
        response.status_code = 404
        response.has_header.return_value = False
        response = middleware.process_response(request, response)
        assert translation.get_language() == language
