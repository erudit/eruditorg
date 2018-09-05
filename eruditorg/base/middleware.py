# -*- coding: utf-8 -*-

import datetime as dt

from django.utils.translation import get_language
from django.utils.translation import LANGUAGE_SESSION_KEY
from django.http import HttpResponsePermanentRedirect
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings


# Originally comes from: https://github.com/divio/django-cms/blob/develop/cms/middleware/language.py
class LanguageCookieMiddleware(MiddlewareMixin):  # pragma: no cover
    """
    This middleware fixes the behaviour of django to determine the language every time from new.
    When you visit / on a page, this middleware saves the current language in a cookie with every
    response.
    """
    def process_response(self, request, response):
        language = get_language()
        if hasattr(request, 'session'):
            session_language = request.session.get(LANGUAGE_SESSION_KEY, None)
            if session_language and not session_language == language:
                request.session[LANGUAGE_SESSION_KEY] = language
                request.session.save()
        if settings.LANGUAGE_COOKIE_NAME in request.COOKIES and \
                request.COOKIES[settings.LANGUAGE_COOKIE_NAME] == language:
            return response
        max_age = 365 * 24 * 60 * 60  # 10 years
        expires = dt.datetime.utcnow() + dt.timedelta(seconds=max_age)
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language, expires=expires)
        return response


class RedirectToFallbackMiddleware(MiddlewareMixin):

    DO_NOT_REDIRECT_NAMESPACES = set((
        'userspace',
        'citations',
        'book',
    ))

    def should_redirect(self, request):
        """ A request should be redirected if the resolver does not
        matched a namespace listed in DO_NOT_REDIRECT_NAMESPACES """
        if not request.resolver_match:
            return True

        namespaces = set(request.resolver_match.namespaces)
        return len(namespaces & self.DO_NOT_REDIRECT_NAMESPACES) == 0

    def process_response(self, request, response):

        if response.status_code == 404 and self.should_redirect(request):
            if request.path[0:4] == '/fr/' or request.path[0:4] == '/en/':
                retro_path = "{}{}".format(settings.FALLBACK_BASE_URL, request.path[3:])
            else:
                retro_path = "{}{}".format(settings.FALLBACK_BASE_URL, request.path)
            return HttpResponsePermanentRedirect(retro_path, )
        return response
