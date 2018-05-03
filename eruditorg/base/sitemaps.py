import datetime as dt

from django.contrib import sitemaps
from django.core.urlresolvers import reverse

from erudit.models import Issue
from erudit.models import Journal
from erudit.solr.models import get_all_articles


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

        class FakePaginator:
            def page(self, number):

                class FakePage:
                    object_list = items

                return FakePage()

        return FakePaginator()

    def items(self):
        return get_all_articles(self.limit, getattr(self, 'page', 1))

    def lastmod(self, obj):
        return dt.datetime.strptime(obj.solr_data['DateAjoutIndex'][:10], '%Y-%m-%d')

    def location(self, obj):
        return obj.get_absolute_url()
