from base.middleware import RedirectToFallbackMiddleware
from django.test import RequestFactory
from unittest import mock


class TestRedirectToFallbackMiddleware(object):

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
