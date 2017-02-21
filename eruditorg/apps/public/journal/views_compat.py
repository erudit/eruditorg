# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import RedirectView

from erudit.models import Article
from erudit.models import Issue
from erudit.models import Journal
from .viewmixins import RedirectExceptionsToFallbackWebsiteMixin


class JournalDetailCheckRedirectView(RedirectExceptionsToFallbackWebsiteMixin, RedirectView):
    permanent = True

    def get_redirect_url(self, *args, **kwargs):

        if 'code' in kwargs:
            get_object_or_404(Journal, code=kwargs['code'])
            return reverse(self.pattern_name, args=[kwargs['code']])
        raise Http404


class IssueDetailRedirectView(RedirectExceptionsToFallbackWebsiteMixin, RedirectView):
    pattern_name = 'public:journal:issue_detail'
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        issue_qs = Issue.objects.select_related('journal').filter(
            Q(journal__code=kwargs['journal_code']) |
            Q(journal__localidentifier=kwargs['journal_code']))
        if 'journal_code' in kwargs and 'localidentifier' in kwargs:
            issue = get_object_or_404(issue_qs, localidentifier=kwargs['localidentifier'])
            return reverse(self.pattern_name, args=[
                kwargs['journal_code'], issue.volume_slug, kwargs['localidentifier'], ])
        elif 'journal_code' in kwargs and 'v' in kwargs and 'n' in kwargs:
            reverse_kwargs = {'number': kwargs['n']} if not kwargs['v'] \
                else {'volume': kwargs['v'], 'number': kwargs['n']}
            issue = get_object_or_404(issue_qs, **reverse_kwargs)
            return reverse(self.pattern_name, args=[
                kwargs['journal_code'], issue.volume_slug, issue.localidentifier, ])
        elif 'journal_code' in kwargs and 'v' in kwargs:
            issue = get_object_or_404(issue_qs, volume=kwargs['v'])
            return reverse(self.pattern_name, args=[
                kwargs['journal_code'], issue.volume_slug, issue.localidentifier, ])
        else:  # pragma: no cover
            raise Http404


class ArticleDetailRedirectView(RedirectExceptionsToFallbackWebsiteMixin, RedirectView):
    pattern_name = 'public:journal:article_detail'
    permanent = True

    def get_redirect_url(self, *args, **kwargs):

        if 'format_identifier' in kwargs and kwargs['format_identifier'] == 'xml':
            self.pattern_name = 'public:journal:article_raw_xml'

        if 'journal_code' in kwargs and 'issue_localid' in kwargs and 'localid' in kwargs:
            article = get_object_or_404(
                Article.objects.select_related('issue', 'issue__journal'),
                localidentifier=kwargs['localid'])
            return reverse(self.pattern_name, kwargs={
                'journal_code': kwargs['journal_code'], 'issue_slug': article.issue.volume_slug,
                'issue_localid': kwargs['issue_localid'], 'localid': kwargs['localid'], })
        elif 'localid' in kwargs:
            article = get_object_or_404(
                Article.objects.select_related('issue', 'issue__journal'),
                localidentifier=kwargs['localid'])
            return reverse(self.pattern_name, kwargs={
                'journal_code': article.issue.journal.code, 'issue_slug': article.issue.volume_slug,
                'issue_localid': article.issue.localidentifier,
                'localid': article.localidentifier, })
        else:  # pragma: no cover
            raise Http404
