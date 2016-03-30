# -*- coding: utf-8 -*-

import logging

from django.core.cache import cache
from django.utils import translation
from django.views.generic import TemplateView
from feedparser import parse as rss_parse

from base.viewmixins import FedoraServiceRequiredMixin
from erudit.models import Issue
# from erudit.models import Journal
from erudit.models import Discipline

logger = logging.getLogger(__name__)


class HomeView(FedoraServiceRequiredMixin, TemplateView):
    """
    This is the main view of the Érudit's public site.
    """
    template_name = 'public/home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)

        # Includes the latest issues
        context['latest_issues'] = Issue.objects.filter(date_published__isnull=False) \
            .select_related('journal').order_by('-date_published')[:8]

        # Includes the 'apropos' news ; note that this is a temporary behavior as
        # these news will likely be included in the new Érudit website in the future.
        context['latest_news'] = self.fetch_apropos_news()

        # Includes some upcoming journals
        # context['upcoming_journals'] = Journal.upcoming_objects.order_by('?')[:3]

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
                assert parsed.get('status') == 200
            except AssertionError:
                # The feed is not available.
                logger.error('Apropos feeds unavailable ({})'.format(feed_url),
                             exc_info=True, extra={'request': self.request, })
                return []
            entries = parsed.get('entries', [])[:6]

            # Stores the entries in the cache
            cache.set(entries_cache_key, entries, 60 * 60)  # 1 hour

        return entries
