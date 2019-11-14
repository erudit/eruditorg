import pytest

from base.sitemaps import JournalSitemap, IssueSitemap, ArticleSitemap

from erudit.test.factories import ArticleFactory, IssueFactory, JournalTypeFactory


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize("is_published, should_be_in_sitemap", [
    (True, True),
    (False, False),
])
def test_published_issues_are_in_sitemap(is_published, should_be_in_sitemap):
    issue = IssueFactory(is_published=is_published)
    assert IssueSitemap().items().filter(pk=issue.pk).exists() == should_be_in_sitemap


@pytest.mark.parametrize("is_published, should_be_in_sitemap", [
    (True, True),
    (False, False),
])
def test_published_articles_are_in_sitemap(is_published, should_be_in_sitemap):
    issue = IssueFactory(is_published=is_published)
    article = ArticleFactory(issue=issue)
    expected = [article.localidentifier] if should_be_in_sitemap else []
    result = [a.localidentifier for a in ArticleSitemap().items()]
    assert result == expected

def test_external_journal_issues_and_articles_are_not_in_sitemaps():
    external_article = ArticleFactory(issue__journal__collection__name='unb')
    assert external_article.issue.journal.code not in JournalSitemap().items()
    assert external_article.issue.localidentifier not in IssueSitemap().items()
    assert external_article.localidentifier not in ArticleSitemap().items()

def test_article_with_non_existing_issue_does_not_raise_exception():
    # RECMA articles hosted on Cairn are indexed in our Solr with the Érudit collection but we don't
    # have the corresponding issues in our database.
    article = ArticleFactory()
    no_issue_article = ArticleFactory()
    no_issue_article.issue.delete()
    assert ArticleSitemap().items() == [article]

def test_scientific_and_cultural_articles_are_in_sitemap():
    scientific_article = ArticleFactory(issue__journal__type=JournalTypeFactory(code='S'))
    cultural_article = ArticleFactory(issue__journal__type=JournalTypeFactory(code='C'))
    assert ArticleSitemap().items() == [scientific_article, cultural_article]
