# -*- coding: utf-8 -*-

import datetime as dt
import structlog
import time

from django.core.cache import cache
from django.utils import translation
from django.views.generic import TemplateView
from django.template import loader
from django.http.response import HttpResponseNotFound, HttpResponseServerError
from feedparser import parse as rss_parse

from erudit.models import Issue
from erudit.models import Journal
from erudit.models import Discipline

logger = structlog.getLogger(__name__)


def internal_error_view(request):
    return HttpResponseServerError(loader.render_to_string('public/500.html', None, request))


def not_found_view(request):
    return HttpResponseNotFound(loader.render_to_string('public/404.html', None, request))


class HomeView(TemplateView):
    """
    This is the main view of the Érudit's public site.
    """
    template_name = 'public/home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)

        # Includes the latest issues
        context['new_journals'] = Journal.objects.filter(is_new=True)
        context['latest_issues'] = Issue.internal_objects.filter(
            date_published__isnull=False, is_published=True) \
            .select_related('journal').order_by('-date_published')[:20]

        # Includes the 'apropos' news ; note that this is a temporary behavior as
        # these news will likely be included in the new Érudit website in the future.
        context['latest_news'] = self.fetch_apropos_news()

        context['disciplines'] = Discipline.objects.order_by('?')

        return context

    def fetch_apropos_news(self):
        """ Retrieves the apropos blog entries and returns them. """
        current_lang = translation.get_language()
        feed_url = 'https://apropos.erudit.org/en/erudit-en/blog/feed/' if current_lang == 'en' \
            else 'https://apropos.erudit.org/fr/erudit/blogue/feed/'

        entries_cache_key = 'apropos-feed-{lang}'.format(lang=current_lang)

        # Tries to fetch previously stored entries
        entries = cache.get(entries_cache_key, None)

        if entries is None:
            # Fetches the blog entries
            try:
                parsed = rss_parse(feed_url)
                status_code = parsed.get('status')
                assert status_code == 200 or status_code == 304
            except AssertionError:
                # The feed is not available.
                logger.error('apropos.unavailable', url=feed_url, request=self.request)
                return []
            entries = parsed.get('entries', [])[:3]

            # Converts the 'published' time struct to a datetime object
            for item in entries:
                item['dt_published'] = dt.datetime.fromtimestamp(time.mktime(item.published_parsed))

            # Stores the entries in the cache
            cache.set(entries_cache_key, entries, 60 * 60)  # 1 hour

        return entries
