# -*- coding: utf-8 -*-

from django.conf import settings


ARTICLE_HTML_CONTENT_USE_CACHE = getattr(
    settings, 'ARTICLE_HTML_CONTENT_USE_CACHE', not settings.DEBUG)

ARTICLE_HTML_CONTENT_CACHE_TIMEOUT = getattr(
    settings, 'ARTICLE_HTML_CONTENT_CACHE_TIMEOUT', 60 * 20)  # 20 minutes
