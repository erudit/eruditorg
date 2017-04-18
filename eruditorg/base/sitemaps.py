# -*- coding: utf-8 -*-

from django.contrib import sitemaps
from django.core.urlresolvers import reverse

from erudit.models import Article
from erudit.models import Issue
from erudit.models import Journal


class JournalSitemap(sitemaps.Sitemap):  # pragma: no cover
    changefreq = 'weekly'
    i18n = True
    limit = 1000
    priority = 0.5

    def items(self):
        return Journal.internal_objects.all()

    def lastmod(self, obj):
        return obj.fedora_updated

    def location(self, obj):
        return reverse('public:journal:journal_detail', args=(obj.code, ))


class IssueSitemap(sitemaps.Sitemap):  # pragma: no cover
    changefreq = 'never'
    i18n = True
    limit = 1000
    priority = 0.5

    def items(self):
        return Issue.internal_objects.select_related('journal').all()

    def lastmod(self, obj):
        return obj.fedora_updated

    def location(self, obj):
        return reverse(
            'public:journal:issue_detail', args=(
                obj.journal.code, obj.volume_slug, obj.localidentifier))


class ArticleSitemap(sitemaps.Sitemap):  # pragma: no cover
    changefreq = 'never'
    i18n = True
    limit = 1000
    priority = 0.5

    def items(self):
        return Article.internal_objects.select_related('issue', 'issue__journal') \
            .filter(publication_allowed=True)

    def lastmod(self, obj):
        return obj.fedora_updated

    def location(self, obj):
        return reverse(
            'public:journal:article_detail', args=(
                obj.issue.journal.code, obj.issue.volume_slug, obj.issue.localidentifier,
                obj.localidentifier))
