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

    def get_start_date(self):
        """ Returns the publication date from which the issues are retrieved. """
        return dt.datetime.now() - dt.timedelta(90)

    def title(self):
        """ Returns the title of the feed. """
        return _("Syndication d'Érudit")

    def description(self):
        """ Returns the description of the feed. """
        start_date_str = dt.datetime.strftime(self.get_start_date(), '%Y/%m/%d')
        today_str = dt.datetime.strftime(dt.datetime.now(), '%Y/%m/%d')
        return '{start_date} - {today}'.format(
            start_date=start_date_str,
            today=today_str,
        )

    def link(self):
        """ Returns the link of the feed's website. """
        return reverse_lazy('public:home')

    def items(self):
        """ Returns the items to embed in the feed. """
        return Issue.objects.filter(
            date_published__gte=self.get_start_date(),
            is_published=True
        ).order_by('-date_published')

    def item_title(self, item):
        """ Returns the title of a feed item. """
        return '{journal_name}, {volume_title}'.format(
            journal_name=item.journal.formatted_title,
            volume_title=item.volume_title,
        )

    def item_description(self, item):
        """ Returns the description of a feed item. """
        return None

    def item_pubdate(self, item):
        """ Returns the publication date of a feed item. """
        return dt.datetime.combine(item.date_published, dt.datetime.min.time())

    def item_link(self, item):
        """ Returns the link of a feed item. """
        return reverse_lazy(
            'public:journal:issue_detail', args=[
                item.journal.code,
                item.volume_slug,
                item.localidentifier,
            ])


class LatestJournalArticlesFeed(Feed):
    """ Provides a list of latest articles associated with a journal. """
    feed_type = EruditRssFeedGenerator

    def get_object(self, request, code=None):
        """ Get the journal's latest issues. """
        journal = Journal.objects.get(Q(code=code) | Q(localidentifier=code))
        self.current_issue = journal.current_issue
        if self.current_issue is None:
            raise Http404()

    def title(self):
        """ Returns the title of the feed. """
        return _("Syndication d'Érudit")

    def description(self):
        """ Returns the description of the feed. """
        return self.current_issue.volume_title

    def link(self):
        """ Returns the link of the feed's website. """
        return reverse_lazy('public:home')

    def items(self, obj):
        return list(self.current_issue.get_articles_from_fedora())

    def item_title(self, item):
        """ Returns the title of a feed item. """
        return item.title

    def item_description(self, item):
        """ Returns the description of a feed item. """
        authors = item.get_formatted_authors()
        abstract = item.abstract
        if authors and not abstract:
            return authors
        elif not authors and abstract:
            return abstract
        else:
            return '{authors}<br />{abstract}'.format(
                authors=authors,
                abstract=abstract,
            )

    def item_link(self, item):
        """ Returns the link of a feed item. """
        return reverse_lazy(
            'public:journal:article_detail', args=[
                item.issue.journal.code,
                item.issue.volume_slug,
                item.issue.localidentifier,
                item.localidentifier,
            ])
