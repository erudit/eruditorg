# -*- coding: utf-8 -*-

from django.conf import settings
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.http.response import HttpResponseRedirect
from django.utils.functional import cached_property

from erudit.models import Article
from erudit.models import Journal

from core.metrics.metric import metric


class RedirectExceptionsToFallbackWebsiteMixin(object):
    """ Mixin that redirects all exceptions to the fallback website """
    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except Http404:
            return HttpResponseRedirect(
                settings.FALLBACK_BASE_URL + self.request.path.strip('/')
            )


class SingleJournalMixin(object):
    """ Simply allows retrieving a Journal instance using its code or localidentifier. """

    def get_journal_queryset(self):
        return Journal.internal_objects.select_related('previous_journal', 'next_journal')

    def get_journal(self):
        try:
            return self.get_journal_queryset().get(
                Q(code=self.kwargs['code']) | Q(localidentifier=self.kwargs['code']))
        except Journal.DoesNotExist:
            raise Http404

    def get_object(self, queryset=None):
        return self.get_journal()

    @cached_property
    def journal(self):
        return self.get_journal()


class ArticleAccessCheckMixin(object):
    """ Defines a way to check whether the current user can browse a given Érudit article. """

    def get_article(self):
        """ Returns the considered article.

        By default the method will try to fetch the article using the ``object`` attribute. If this
        attribute is not available the
        :meth:`get_object<django:django.views.generic.detail.SingleObjectMixin.get_object>` method
        will be used. But subclasses can override this to control the way the article is retrieved.
        """
        return self.object if hasattr(self, 'object') else self.get_object()

    def get_context_data(self, **kwargs):
        """ Inserts a flag indicating if the article can be accessed in the context. """
        context = super(ArticleAccessCheckMixin, self).get_context_data(**kwargs)
        context['article_access_granted'] = self.article_access_granted
        return context

    def has_access(self):
        """ Returns a boolean indicating if the article can be accessed.

        The following verifications are performed in order to determine if an article
        can be browsed:

            1- it is in open access
            2- the current user has access to it with its individual account
            3- the current IP address is inside on of the IP address ranges allowed
               to access to it
        """
        article = self.get_article()

        # 1- Is the article in open access? Is the article subject to a movable limitation?
        if article.open_access or not article.embargoed:
            return True

        if not self.request.subscription:
            return False

        return self.request.subscription.provides_access_to(article)

    @cached_property
    def article_access_granted(self):
        return self.has_access()


class SingleArticleMixin(object):
    """ Simply allows retrieving an Article instance. """

    def get_object(self, queryset=None):
        queryset = Article.internal_objects.all() if queryset is None else queryset
        queryset = queryset \
            .prefetch_related('abstracts', 'authors', 'authors__affiliations')
        return get_object_or_404(queryset, localidentifier=self.kwargs['localid'])


class SingleArticleWithScholarMetadataMixin(SingleArticleMixin):
    """ Add Google Scholar Metadata to the context """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.get_object()
        context['citation_title_metadata'] = article.title
        context['citation_journal_title_metadata'] = article.get_erudit_object()\
            .get_formatted_journal_title()
        context['citation_references'] = article.get_erudit_object()\
            .get_references(strip_markup=True)
        return context


class ArticleViewMetricCaptureMixin(object):
    tracking_article_view_granted_metric_name = 'erudit__journal__article_view'
    tracking_view_type = 'html'

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        response = super(ArticleViewMetricCaptureMixin, self).dispatch(request, *args, **kwargs)
        if response.status_code == 200 and self.article_access_granted:
            # We register this metric only if the article can be viewed
            metric(
                self.tracking_article_view_granted_metric_name,
                tags=self.get_metric_tags(), **self.get_metric_fields())
        return response

    def get_metric_fields(self):
        article = self.get_article()
        subscription = self.request.subscription
        return {
            'issue_localidentifier': article.issue.localidentifier,
            'localidentifier': article.localidentifier,
            'subscription_id': subscription.id if subscription else None,
        }

    def get_metric_tags(self):
        article = self.get_article()
        return {
            'journal_localidentifier': article.issue.journal.localidentifier,
            'open_access': article.open_access or not article.embargoed,
            'view_type': self.get_tracking_view_type(),
        }

    def get_tracking_view_type(self):
        return self.tracking_view_type
