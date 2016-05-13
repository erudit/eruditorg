# -*- coding: utf-8 -*-

from django.http import Http404

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
