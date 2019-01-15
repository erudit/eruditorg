import datetime as dt

from django.contrib.syndication.views import Feed
from django.urls import reverse_lazy
from django.db.models import Q
from django.http import Http404
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

    def item_link(self, item):
        """ Returns the link of a feed item. """
        return reverse_lazy(
            'public:journal:issue_detail',
            args=[item.journal.code, item.volume_slug, item.localidentifier])

    def items(self):
        """ Returns the items to embed in the feed. """
        return Issue.objects.filter(
            date_published__gte=self.get_start_date(),
            is_published=True
        ).order_by('-date_published')


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

    def get_object(self, request, code=None):
        """ Get the journal's latest issues. """
        self.journal = Journal.objects.get(Q(code=code) | Q(localidentifier=code))
        self.last_issue = self.journal.last_issue
        if self.last_issue is None:
            raise Http404()

    def get_context_data(self, **kwargs):
        context = super(LatestJournalArticlesFeed, self).get_context_data(**kwargs)
        obj = context.get('obj')

        context['authors'] = obj.get_formatted_authors()
        context['abstract'] = obj.abstract

        return context

    def item_link(self, item):
        """ Returns the link of a feed item. """
        return reverse_lazy(
            'public:journal:article_detail',
            args=[
                item.issue.journal.code, item.issue.volume_slug, item.issue.localidentifier,
                item.localidentifier])

    def items(self, obj):
        return list(self.last_issue.get_articles_from_fedora())
