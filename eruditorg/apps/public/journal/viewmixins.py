# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404

from core.metrics.metric import metric
from erudit.models import Article


class SingleArticleMixin(object):
    def get_object(self, queryset=None):
        queryset = Article.objects.all() if queryset is None else queryset
        return get_object_or_404(queryset, localidentifier=self.kwargs['localid'])


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
