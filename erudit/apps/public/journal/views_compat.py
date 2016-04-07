# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import RedirectView

from erudit.models import Article
from erudit.models import Issue


class IssueDetailRedirectView(RedirectView):
    pattern_name = 'public:journal:issue-detail'
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        issue_qs = Issue.objects.select_related('journal').filter(
            Q(journal__code=kwargs['journal_code']) |
            Q(journal__localidentifier=kwargs['journal_code']))
        if 'journal_code' in kwargs and 'localidentifier' in kwargs:
            return reverse(self.pattern_name, kwargs={
                'journal_code': kwargs['journal_code'],
                'localidentifier': kwargs['localidentifier'], })
        elif 'journal_code' in kwargs and 'v' in kwargs and 'n' in kwargs:
            issue = get_object_or_404(issue_qs, volume=kwargs['v'], number=kwargs['n'])
            return reverse(self.pattern_name, kwargs={
                'journal_code': kwargs['journal_code'],
                'localidentifier': issue.localidentifier, })
        elif 'journal_code' in kwargs and 'v' in kwargs:
            issue = get_object_or_404(issue_qs, volume=kwargs['v'])
            return reverse(self.pattern_name, kwargs={
                'journal_code': kwargs['journal_code'],
                'localidentifier': issue.localidentifier, })
        else:  # pragma: no cover
            raise Http404


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
        else:  # pragma: no cover
            raise Http404
