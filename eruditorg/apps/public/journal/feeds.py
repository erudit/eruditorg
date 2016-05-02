# -*- coding: utf-8 -*-

import datetime as dt

from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.utils import translation
from django.utils.translation import gettext as _

from base.feedgenerator import EruditRssFeedGenerator
from erudit.models import Article
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


class LatestJournalArticlesFeed(Feed):
    """ Provides a list of latest articles associated with a journal. """
    feed_type = EruditRssFeedGenerator

    # Standard RSS elements
    title = _("Syndication d'Érudit")
    link = reverse_lazy('public:home')

    # Item elements
    title_template = 'public/journal/feeds/latest_journal_articles_title.html'
    description_template = 'public/journal/feeds/latest_journal_articles_description.html'

    def description(self):
        """ Returns the feed's description as a normal Python string. """
        return self.last_issue.volume_title

    def get_object(self, request, journal_code=None):
        """ Get the journal's latest issues. """
        self.journal = Journal.objects.get(Q(code=journal_code) | Q(localidentifier=journal_code))
        self.last_issue = self.journal.last_issue

    def get_context_data(self, **kwargs):
        context = super(LatestJournalArticlesFeed, self).get_context_data(**kwargs)
        obj = context.get('obj')

        context['authors'] = obj.authors.all()

        abstracts = obj.erudit_object.abstracts
        lang = translation.get_language()
        _abstracts = list(filter(lambda r: r['lang'] == lang, abstracts))
        _abstract_lang = _abstracts[0]['content'] if len(_abstracts) else None
        _abstract = abstracts[0]['content'] if len(abstracts) else None
        context['abstract'] = _abstract_lang or _abstract

        return context

    def items(self, obj):
        articles = Article.objects.filter(issue_id=self.last_issue)
        return sorted(articles, key=lambda a: a.erudit_object.ordseq)
