# -*- coding: utf-8 -*-

import datetime as dt

from django.utils.translation import get_language
from django.utils.translation import LANGUAGE_SESSION_KEY
from django.http import HttpResponsePermanentRedirect
from django.conf import settings


# Originally comes from: https://github.com/divio/django-cms/blob/develop/cms/middleware/language.py
class LanguageCookieMiddleware(object):  # pragma: no cover
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


class RedirectToFallbackMiddleware(object):

    def process_response(self, request, response):
        if response.status_code == 404:
            if request.path[0:4] == '/fr/' or request.path[0:4] == '/en/':
                retro_path = "{}{}".format(settings.FALLBACK_BASE_URL, request.path[3:])
            else:
                retro_path = "{}{}".format(settings.FALLBACK_BASE_URL, request.path)
            return HttpResponsePermanentRedirect(retro_path, )
        return response
