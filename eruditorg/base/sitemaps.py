import datetime as dt
from math import ceil

from django.contrib import sitemaps
from django.urls import reverse

from erudit.models import Issue
from erudit.models import Journal
from erudit.solr.models import (
    get_all_articles,
    get_total_number_of_articles,
)


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
        return Issue.internal_objects.select_related('journal').filter(is_published=True)

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

    def get_urls(self, page=1, *args, **kwargs):
        self.page = int(page)
        return super().get_urls(page, *args, **kwargs)

    @property
    def paginator(self):
        items = self.items()
        hits = self.hits()

        class FakePaginator:
            per_page = self.limit

            @staticmethod
            def page(number):

                class FakePage:
                    object_list = items

                return FakePage()

            @property
            def num_pages(self):
                return int(ceil(hits / float(self.per_page)))

        return FakePaginator()

    def items(self):
        return get_all_articles(self.limit, getattr(self, 'page', 1))

    @staticmethod
    def hits():
        return get_total_number_of_articles()

    @staticmethod
    def lastmod(obj):
        return dt.datetime.strptime(obj.solr_data['DateAjoutIndex'][:10], '%Y-%m-%d')

    def location(self, obj):
        return reverse(
            'public:journal:article_detail', args=(
                obj.issue.journal.code,
                obj.issue.volume_slug,
                obj.issue.localidentifier,
                obj.localidentifier,
            )
        )
