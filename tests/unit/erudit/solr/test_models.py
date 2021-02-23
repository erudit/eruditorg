import pysolr
import pytest

from erudit.solr.models import Article, SolrDocument
from erudit.test.factories import IssueFactory


class TestSolrDocument:
    def test_localidentfier_doesnt_include_unb_prefix(self):
        assert SolrDocument({"ID": "unb:123", "Corpus_fac": "Article"}).localidentifier == "123"
        assert SolrDocument({"ID": "123", "Corpus_fac": "Article"}).localidentifier == "123"

    def test_solr_id_does_include_unb_prefix(self):
        assert SolrDocument({"ID": "unb:123", "Corpus_fac": "Article"}).solr_id == "unb:123"
        assert SolrDocument({"ID": "123", "Corpus_fac": "Article"}).solr_id == "123"


@pytest.mark.django_db
class TestArticle:
    @pytest.mark.parametrize(
        "issue_exist, external_url, expected_url",
        (
            (False, None, None),
            (True, None, "/fr/revues/journal/2020-issue/"),
            (True, "https://www.exemple.com", "https://www.exemple.com"),
        ),
    )
    def test_issue_url(self, issue_exist, external_url, expected_url):
        if issue_exist:
            IssueFactory(
                journal__code="journal",
                localidentifier="issue",
                year="2020",
                external_url=external_url,
            )
        article = Article(
            {
                "ID": "article",
                "NumeroID": "issue",
                "RevueID": "journal",
            }
        )
        assert article.issue_url == expected_url
