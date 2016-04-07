# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import RedirectView

from erudit.models import Article


class IssueDetailRedirectView(RedirectView):
    pattern_name = 'public:journal:issue-detail'
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        url_kwargs = {k: v for k, v in kwargs.items() if k in ['journal_code', 'localidentifier']}
        return reverse(self.pattern_name, kwargs=url_kwargs)


class ArticleDetailRedirectView(RedirectView):
    pattern_name = 'public:journal:article-detail'
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        if 'journal_code' in kwargs and 'issue_localid' in kwargs and 'localid' in kwargs:
            return reverse(self.pattern_name, kwargs={
                'journal_code': kwargs['journal_code'], 'issue_localid': kwargs['issue_localid'],
                'localid': kwargs['localid'], })
        elif 'localid' in kwargs:
            article = get_object_or_404(
                Article.objects.select_related('issue', 'issue__journal'),
                localidentifier=kwargs['localid'])
            return reverse(self.pattern_name, kwargs={
                'journal_code': article.issue.journal.code,
                'issue_localid': article.issue.localidentifier,
                'localid': article.localidentifier, })
        else:
            raise Http404
