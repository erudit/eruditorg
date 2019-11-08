import structlog

from django.urls import translate_url
from django.utils import translation
from django.utils.deprecation import MiddlewareMixin
from django.middleware.locale import LocaleMiddleware
import datetime as dt

from django.utils.translation import get_language
from django.utils.translation import LANGUAGE_SESSION_KEY
from django.conf import settings


logger = structlog.get_logger(__name__)


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


class PolyglotLocaleMiddleware(LocaleMiddleware):
    """
    Extends LocaleMiddleware to:

    1. Try to find the language in which the pattern exists
    2. If the pattern exists, translate it to the user's language
    """
    def process_response(self, request, response):
        if response.status_code == 404:
            user_lang = translation.get_language()
            for language, _ in settings.LANGUAGES:
                with translation.override(language):
                    resp = super().process_response(request, response)
                    if resp.status_code != 404:
                        return self.response_redirect_class(translate_url(resp.url, user_lang))
        return response


class LogHttp404Middleware(MiddlewareMixin):
    def process_response(self, request, response):
        if response.status_code == 404:
            logger.warn('http_404', path=request.path)
        return response
