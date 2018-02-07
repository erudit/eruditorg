import pytest

from base.sitemaps import IssueSitemap, ArticleSitemap

from erudit.test.factories import ArticleFactory, IssueFactory


@pytest.mark.django_db
class TestSitemaps:

    @pytest.mark.parametrize("is_published, should_be_in_sitemap", [
        (True, True),
        (False, False),
    ])
    def test_published_issues_are_in_sitemap(self, is_published, should_be_in_sitemap):
        issue = IssueFactory(is_published=is_published)
        assert IssueSitemap().items().filter(pk=issue.pk).exists() == should_be_in_sitemap

    @pytest.mark.parametrize("is_published, should_be_in_sitemap", [
        (True, True),
        (False, False),
    ])
    def test_published_articles_are_in_sitemap(self, is_published, should_be_in_sitemap):
        issue = IssueFactory(is_published=is_published)
        article = ArticleFactory(issue=issue)
        assert ArticleSitemap().items().filter(pk=article.pk).exists() == should_be_in_sitemap
