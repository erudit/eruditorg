import pytest
from base.middleware import RedirectToFallbackMiddleware, PolyglotLocaleMiddleware
from django.test import RequestFactory
from django.http.response import HttpResponse
from django.utils import translation
from erudit.test.factories import ArticleFactory

from unittest import mock


class TestRedirectToFallbackMiddleware:

    def test_can_redirect_urls_that_does_not_resolve(self):
        middleware = RedirectToFallbackMiddleware()
        request = RequestFactory().get('/sdfdsfdsf/')
        response = mock.Mock()
        response.status_code = 404
        response = middleware.process_response(request, response)

        assert request.resolver_match == None
        assert response.status_code == 301


    def test_can_redirect_urls_that_resolve(self):
        middleware = RedirectToFallbackMiddleware()
        request = RequestFactory().get('/fr/revues/')
        request.resolver_match = mock.Mock()
        request.resolver_match.namespaces = ['journal']
        response = mock.Mock()
        response.status_code = 404
        response = middleware.process_response(request, response)

        assert response.status_code == 301

    def test_does_not_redirect_urls_in_do_not_redirect_list(self):
        middleware = RedirectToFallbackMiddleware()
        request = RequestFactory().get('/fr/espace-utilisateur/')
        request.resolver_match = mock.Mock()
        request.resolver_match.namespaces = ['userspace']

        response = mock.Mock()
        response.status_code = 404
        response = middleware.process_response(request, response)

        assert response.status_code == 404


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
