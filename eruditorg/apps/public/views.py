# -*- coding: utf-8 -*-

import datetime as dt
import structlog
import time

from collections import defaultdict
from django.conf import settings
from django.core.cache import cache
from django.utils import translation
from django.views.generic import TemplateView
from django.template import loader
from django.http.response import (
    HttpResponseForbidden,
    HttpResponseNotFound,
    HttpResponseServerError,
)
from feedparser import parse as rss_parse

from erudit.models import Issue
from erudit.models import Journal
from erudit.models import Discipline

logger = structlog.getLogger(__name__)


def internal_error_view(request, exception=None):
    return HttpResponseServerError(loader.render_to_string("public/500.html", None, request))


def not_found_view(request, exception=None):
    return HttpResponseNotFound(loader.render_to_string("public/404.html", None, request))


def forbidden_view(request, exception=None):
    return HttpResponseForbidden(loader.render_to_string("public/403.html", None, request))


def forbidden_view_csrf(request, reason=""):
    return HttpResponseForbidden(loader.render_to_string("public/403.html", None, request))


class HomeView(TemplateView):
    """
    This is the main view of the Érudit's public site.
    """

    template_name = "public/home.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)

        # Includes the latest journals
        context["new_journals"] = (
            Journal.objects.prefetch_related(
                "disciplines",
                "information",
            )
            .filter(
                is_new=True,
                year_of_addition__isnull=False,
            )
            .order_by("?")
        )

        # Includes the latest issues
        latest_issues = (
            Issue.internal_objects.prefetch_related(
                "journal__collection",
                "journal__disciplines",
            )
            .select_related(
                "journal",
            )
            .filter(
                date_published__gte=dt.datetime.now() - dt.timedelta(days=60),
                is_published=True,
            )
            .order_by("-date_published", "journal_id")
        )

        issues = defaultdict(list)
        for issue in latest_issues:
            # If the issue's year is at least two years older than the issue's published date, we
            # can assume it's a retrospective issue and we should group it with other retrospective
            # issues from the same journal.
            if issue.year < issue.date_published.year - 1:
                issues[issue.journal.localidentifier].append(issue)
            # If the issue's year is the same or one year older than the issue's published date, we
            # can assume it's a current issue and we should not group it with other issues from the
            # same journal.
            else:
                issues[issue.localidentifier].append(issue)
            # Limit latest issues to 20.
            if len(issues) >= 20:
                break
        # Cast the defaultdict to a dict because Django templates can't iterate on a defaultdict.
        context["latest_issues"] = dict(issues)

        # Includes the 'apropos' news ; note that this is a temporary behavior as
        # these news will likely be included in the new Érudit website in the future.
        context["latest_news"] = self.fetch_apropos_news()

        context["disciplines"] = Discipline.objects.order_by("?")

        return context

    def fetch_apropos_news(self):
        """ Retrieves the apropos blog entries and returns them. """
        current_lang = translation.get_language()
        feed_url = (
            "https://apropos.erudit.org/en/erudit-en/blog/feed/"
            if current_lang == "en"
            else "https://apropos.erudit.org/fr/erudit/blogue/feed/"
        )

        entries_cache_key = "apropos-feed-{lang}".format(lang=current_lang)

        # Tries to fetch previously stored entries
        entries = cache.get(entries_cache_key, None)

        if entries is None:
            # Fetches the blog entries
            try:
                parsed = rss_parse(feed_url)
                status_code = parsed.get("status")
                assert status_code == 200 or status_code == 304
            except AssertionError:
                # The feed is not available.
                logger.error("apropos.unavailable", url=feed_url, request=self.request)
                return []
            entries = parsed.get("entries", [])[:3]

            # Converts the 'published' time struct to a datetime object
            for item in entries:
                item["dt_published"] = dt.datetime.fromtimestamp(time.mktime(item.published_parsed))

            # Stores the entries in the cache
            cache.set(entries_cache_key, entries, settings.SHORT_TTL)  # 1 hour

        return entries
