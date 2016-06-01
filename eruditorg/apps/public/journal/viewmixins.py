# -*- coding: utf-8 -*-

from django.http import Http404

from core.tracking.metric import metric
from erudit.models import Article


class SingleArticleMixin(object):
    def get_object(self, queryset=None):
        queryset = Article.objects.all() if queryset is None else queryset
        queryset.select_related('issue', 'issue__journal').prefetch_related('authors')
        if 'pk' in self.kwargs:
            return super(SingleArticleMixin, self).get_object(queryset)

        try:
            return Article.objects.get(localidentifier=self.kwargs['localid'])
        except Article.DoesNotExist:
            raise Http404


class ArticleViewTrackingMetricMixin(object):
    tracking_article_view_granted_metric_name = 'erudit__journal__article_view'
    tracking_view_type = 'html'

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        response = super(ArticleViewTrackingMetricMixin, self).dispatch(request, *args, **kwargs)
        if response.status_code == 200 and self.article_access_granted:
            # We register this metric only if the article can be viewed
            metric(
                self.tracking_article_view_granted_metric_name,
                tags=self.get_metric_tags(), **self.get_metric_fields())
        return response

    def get_metric_fields(self):
        article = self.get_article()
        subscription = self.subscription
        return {
            'issue_localidentifier': article.issue.localidentifier,
            'localidentifier': article.localidentifier,
            'subscription_id': subscription.id if subscription else None,
        }

    def get_metric_tags(self):
        article = self.get_article()
        return {
            'journal_localidentifier': article.issue.journal.localidentifier,
            'open_access': article.open_access or not article.has_movable_limitation,
            'view_type': self.get_tracking_view_type(),
        }

    def get_tracking_view_type(self):
        return self.tracking_view_type
