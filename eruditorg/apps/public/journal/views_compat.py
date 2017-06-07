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
from base.viewmixins import ActivateLegacyLanguageViewMixin


class JournalDetailCheckRedirectView(
    RedirectExceptionsToFallbackWebsiteMixin, RedirectView,
    ActivateLegacyLanguageViewMixin
):
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        self.activate_legacy_language(*args, **kwargs)

        if 'code' in kwargs:
            journal = Journal.legacy_objects.get_by_id_or_404(
                kwargs['code']
            )
            return reverse(
                'public:journal:journal_detail', args=[
                    journal.code,
                ]
            ) if journal.last_issue \
                else reverse(self.pattern_name, args=[journal.code])
        raise Http404


class IssueDetailRedirectView(
    RedirectExceptionsToFallbackWebsiteMixin, RedirectView, ActivateLegacyLanguageViewMixin
):
    pattern_name = 'public:journal:issue_detail'
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        self.activate_legacy_language(*args, **kwargs)
        issue_qs = Issue.objects.select_related('journal').filter(
            Q(journal__code=kwargs['journal_code']) |
            Q(journal__localidentifier=kwargs['journal_code']))
        if 'journal_code' in kwargs and 'localidentifier' in kwargs:
            issue = get_object_or_404(issue_qs, localidentifier=kwargs['localidentifier'])
            return reverse(self.pattern_name, args=[
                kwargs['journal_code'], issue.volume_slug, kwargs['localidentifier'], ])
        elif 'journal_code' in kwargs and 'v' in kwargs and 'n' in kwargs:
            additional_filter = (Q(number=kwargs['n']) | Q(localidentifier=kwargs['n']))
            if kwargs['v']:
                additional_filter &= Q(volume=kwargs['v'])
            if 'year' in kwargs:
                additional_filter &= Q(year=kwargs['year'])
            if kwargs['v']:
                issue = get_object_or_404(issue_qs, additional_filter)
            else:
                issue = issue_qs.filter(additional_filter).last()
            if not issue:
                raise Http404
            return reverse(self.pattern_name, args=[
                kwargs['journal_code'], issue.volume_slug, issue.localidentifier, ])
        elif 'journal_code' in kwargs and 'v' in kwargs and 'year' in kwargs:
            issue = issue_qs.filter(volume=kwargs['v'], year=kwargs['year']).last()
            if not issue:
                raise Http404
            return reverse(self.pattern_name, args=[
                kwargs['journal_code'], issue.volume_slug, issue.localidentifier,
            ])
        elif 'journal_code' in kwargs and 'v' in kwargs:
            issue = get_object_or_404(issue_qs, volume=kwargs['v'])
            return reverse(self.pattern_name, args=[
                kwargs['journal_code'], issue.volume_slug, issue.localidentifier, ])
        else:  # pragma: no cover
            raise Http404


class ArticleDetailRedirectView(
    ActivateLegacyLanguageViewMixin, RedirectExceptionsToFallbackWebsiteMixin,
    RedirectView
):
    pattern_name = 'public:journal:article_detail'
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        self.activate_legacy_language(*args, **kwargs)
        if 'format_identifier' in kwargs and kwargs['format_identifier'] == 'xml':
            self.pattern_name = 'public:journal:article_raw_xml'

        if 'format_identifier' in kwargs and kwargs['format_identifier'] == 'pdf':
            self.pattern_name = 'public:journal:article_raw_pdf'
        if 'localid' in kwargs:
            article = get_object_or_404(
                Article.objects.select_related('issue', 'issue__journal'),
                localidentifier=kwargs['localid'])
            return reverse(self.pattern_name, kwargs={
                'journal_code': article.issue.journal.code, 'issue_slug': article.issue.volume_slug,
                'issue_localid': article.issue.localidentifier,
                'localid': article.localidentifier, })
        else:  # pragma: no cover
            raise Http404
