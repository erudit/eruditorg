# -*- coding: utf-8 -*-

import datetime as dt

from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.utils.translation import gettext as _

from base.feedgenerator import EruditRssFeedGenerator
from erudit.models import Issue
from erudit.models import Journal


class LatestIssuesFeed(Feed):
    """ Provides a list of latest issues published on Érudit. """
    feed_type = EruditRssFeedGenerator

    # Standard RSS elements
    title = _("Syndication d'Érudit")
    link = reverse_lazy('public:home')

    # Item elements
    title_template = 'public/journal/feeds/latest_issues_title.html'
    description_template = 'public/journal/feeds/latest_issues_description.html'

    days_delta = 90

    def get_start_date(self):
        """ Returns the publication date from which the issues are retrieved. """
        return (dt.datetime.now() + dt.timedelta(-self.days_delta))

    def description(self, obj):
        """ Returns the description of the feed. """
        start_date_str = dt.datetime.strftime(self.get_start_date(), '%Y/%m/%d')
        today_str = dt.datetime.strftime(dt.datetime.now(), '%Y/%m/%d')
        return '{start_date} - {today}'.format(start_date=start_date_str, today=today_str)

    def items(self):
        """ Returns the items to embed in the feed. """
        return Issue.objects.filter(date_published__gte=self.get_start_date()) \
            .order_by('-date_published')


class LatestJournalIssueArticlesFeed(Feed):
    title = _("Syndication d'Érudit")
    link = 'http://www.erudit.org'

    def get_object(self, request, journal_code=None):
        """ Get the journal's latest issues. """
        try:
            return Journal.objects.get(
                Q(code=journal_code) | Q(localidentifier=journal_code)).last_issue
        except:
            return None

    def title(self, obj):
        return _("Érudit | ")

    def description(self, obj):
        return "{year} V{volume} N{number}".format(
            year=obj.year, volume=obj.volume, number=obj.number
        )

    def link(self, obj):
        return obj.get_absolute_url()

    def items(self, obj):
        return obj.issues.all()

    def item_title(self, item):
        return item.title

    def item_description(self, obj):
        return ",".join([str(author) for author in obj.authors.all()])
