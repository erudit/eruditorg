import pytest

from django.test import override_settings

from erudit.models.journal import Article
from erudit.solr.models import ExternalArticle, InternalArticle, SolrDocument
from erudit.test.factories import IssueFactory, JournalFactory


class TestSolrDocument:
    def test_localidentfier_doesnt_include_unb_prefix(self):
        assert SolrDocument({"ID": "unb:123", "Corpus_fac": "Article"}).localidentifier == "123"
        assert SolrDocument({"ID": "123", "Corpus_fac": "Article"}).localidentifier == "123"

    def test_solr_id_does_include_unb_prefix(self):
        assert SolrDocument({"ID": "unb:123", "Corpus_fac": "Article"}).solr_id == "unb:123"
        assert SolrDocument({"ID": "123", "Corpus_fac": "Article"}).solr_id == "123"


@pytest.mark.django_db
class TestExternalArticle:
    @pytest.mark.parametrize(
        "solr_data, expected_article_type",
        (
            ({"ID": "article"}, "article"),
            ({"ID": "article", "TypeArticle_fac": "Compterendu"}, "compterendu"),
            ({"ID": "article", "TypeArticle_fac": "Compte rendu"}, "compterendu"),
            ({"ID": "article", "TypeArticle_fac": "Autre"}, "autre"),
            ({"ID": "article", "TypeArticle_fac": "Note"}, "note"),
            ({"ID": "article", "TypeArticle_fac": "foo"}, "article"),
        ),
    )
    def test_article_type(self, solr_data, expected_article_type):
        article = ExternalArticle(solr_data)
        assert article.article_type == expected_article_type

    @pytest.mark.parametrize(
        "solr_data, expected_article_type_display",
        (
            ({"ID": "article"}, Article.TYPE_DISPLAY["article"]),
            (
                {"ID": "article", "TypeArticle_fac": "Compterendu"},
                Article.TYPE_DISPLAY["compterendu"],
            ),
            (
                {"ID": "article", "TypeArticle_fac": "Compte rendu"},
                Article.TYPE_DISPLAY["compterendu"],
            ),
            ({"ID": "article", "TypeArticle_fac": "Autre"}, Article.TYPE_DISPLAY["autre"]),
            ({"ID": "article", "TypeArticle_fac": "Note"}, Article.TYPE_DISPLAY["note"]),
            ({"ID": "article", "TypeArticle_fac": "foo"}, Article.TYPE_DISPLAY["article"]),
        ),
    )
    def test_type_display(self, solr_data, expected_article_type_display):
        article = ExternalArticle(solr_data)
        assert article.type_display == expected_article_type_display

    def test_journal_type(self):
        article = ExternalArticle(
            {
                "ID": "article",
            }
        )
        assert article.journal_type == "S"

    @pytest.mark.parametrize(
        "external_url, expected_url",
        (
            (None, "/fr/revues/journal/"),
            ("https://www.exemple.com", "https://www.exemple.com"),
        ),
    )
    def test_journal_url(self, external_url, expected_url):
        JournalFactory(
            code="journal",
            external_url=external_url,
        )
        article = ExternalArticle(
            {
                "ID": "article",
                "RevueID": "journal",
                "Fonds_fac": "Érudit",
            }
        )
        assert article.journal_url == expected_url

    def test_issue_url(self):
        article = ExternalArticle(
            {
                "ID": "article",
            }
        )
        assert article.issue_url is None

    def test_can_cite(self):
        article = ExternalArticle(
            {
                "ID": "article",
            }
        )
        assert not article.can_cite

    @pytest.mark.parametrize(
        "keywords",
        ([], ["Mot clé", "Keyword"]),
    )
    def test_keywords(self, keywords):
        article = ExternalArticle({"ID": "article", "MotsCles": keywords})
        assert article.keywords == keywords

    @pytest.mark.parametrize(
        "keywords, expected_keywords_display",
        (
            ([], ""),
            (["Mot clé"], "Mot clé"),
            (["Mot clé", "Keyword"], "Mot clé, Keyword"),
        ),
    )
    def test_keywords_display(self, keywords, expected_keywords_display):
        article = ExternalArticle({"ID": "article", "MotsCles": keywords})
        assert article.keywords_display == expected_keywords_display

    @pytest.mark.parametrize(
        "langcode, expected_abstract",
        (
            ("fr", "Résumé français"),
            ("en", "English abstract"),
            ("es", "Resumen en español"),
            ("it", None),
        ),
    )
    def test_abstract(self, langcode, expected_abstract):
        article = ExternalArticle(
            {
                "ID": "article",
                "Resume_fr": "Résumé français",
                "Resume_en": "English abstract",
                "Resume_es": "Resumen en español",
            }
        )
        with override_settings(LANGUAGE_CODE=langcode):
            assert article.abstract == expected_abstract


@pytest.mark.django_db
class TestInternalArticle:
    @pytest.mark.parametrize(
        "journal_type",
        ("S", "C"),
    )
    def test_journal_type(self, journal_type):
        issue = IssueFactory(journal__type_code=journal_type, localidentifier="issue")
        article = InternalArticle(
            {
                "ID": "article",
            },
            issue,
        )
        assert article.journal_type == journal_type

    @pytest.mark.parametrize(
        "external_url, expected_url",
        (
            (None, "/fr/revues/journal/"),
            ("https://www.exemple.com", "https://www.exemple.com"),
        ),
    )
    def test_journal_url(self, external_url, expected_url):
        issue = IssueFactory(
            journal__code="journal", journal__external_url=external_url, localidentifier="issue"
        )
        article = InternalArticle(
            {
                "ID": "article",
            },
            issue,
        )
        assert article.journal_url == expected_url

    @pytest.mark.parametrize(
        "external_url, expected_url",
        (
            (None, "/fr/revues/journal/2020-issue/"),
            ("https://www.exemple.com", "https://www.exemple.com"),
        ),
    )
    def test_issue_url(self, external_url, expected_url):
        issue = IssueFactory(
            journal__code="journal",
            localidentifier="issue",
            year="2020",
            external_url=external_url,
        )
        article = InternalArticle(
            {
                "ID": "article",
            },
            issue,
        )
        assert article.issue_url == expected_url

    @pytest.mark.parametrize(
        "external_url, url_document, expected_url",
        (
            (None, "http://id.erudit.org", "/fr/revues/journal/2020-issue/article/"),
            (None, "https://www.exemple.com", "https://www.exemple.com"),
            ("https://www.exemple.com", "https://www.exemple.com", "https://www.exemple.com"),
        ),
    )
    def test_url(self, external_url, url_document, expected_url):
        issue = IssueFactory(
            journal__code="journal",
            localidentifier="issue",
            year="2020",
            external_url=external_url,
        )
        article = InternalArticle(
            {
                "ID": "article",
                "URLDocument": [url_document],
            },
            issue,
        )
        assert article.url == expected_url

    @pytest.mark.parametrize(
        "external_url, url_document, expected_url",
        (
            (None, "http://id.erudit.org", "/fr/revues/journal/2020-issue/article.pdf"),
            (None, "https://www.exemple.com", None),
            ("https://www.exemple.com", "https://www.exemple.com", None),
        ),
    )
    def test_pdf_url(self, external_url, url_document, expected_url):
        issue = IssueFactory(
            journal__code="journal",
            localidentifier="issue",
            year="2020",
            external_url=external_url,
        )
        article = InternalArticle(
            {
                "ID": "article",
                "URLDocument": [url_document],
            },
            issue,
        )
        assert article.pdf_url == expected_url

    @pytest.mark.parametrize(
        "external_url, expected_url",
        (
            (None, "/fr/revues/journal/2020-issue/article/ajax-citation-modal"),
            ("https://www.exemple.com", None),
        ),
    )
    def test_ajax_citation_modal_url(self, external_url, expected_url):
        issue = IssueFactory(
            journal__code="journal",
            localidentifier="issue",
            year="2020",
            external_url=external_url,
        )
        article = InternalArticle(
            {
                "ID": "article",
            },
            issue,
        )
        assert article.ajax_citation_modal_url == expected_url

    @pytest.mark.parametrize(
        "has_fedora_created",
        (True, False),
    )
    def test_can_cite(self, has_fedora_created):
        issue = IssueFactory(localidentifier="issue")
        if not has_fedora_created:
            issue._meta.get_field("fedora_created").auto_now = False
            issue.fedora_created = None
            issue.save()
            issue._meta.get_field("fedora_created").auto_now = True
        article = InternalArticle(
            {
                "ID": "article",
            },
            issue,
        )
        assert article.can_cite == has_fedora_created
