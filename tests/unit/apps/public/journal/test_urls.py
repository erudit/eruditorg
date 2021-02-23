import pytest

from django.urls import resolve
from django.urls.exceptions import Resolver404


class TestJournalUrlPatterns:
    @pytest.mark.parametrize(
        "url, expected_url_name",
        [
            # Article raw XML.
            ("/fr/revues/journal/2020-issue/article.xml", "article_raw_xml"),
            ("/fr/revues/journal/2020-issue/article/foo.xml", False),
            ("/fr/revues/journal/2020-issue/article.xmlfoo", False),
            # Article raw PDF.
            ("/fr/revues/journal/2020-issue/article.pdf", "article_raw_pdf"),
            ("/fr/revues/journal/2020-issue/article/foo.pdf", False),
            ("/fr/revues/journal/2020-issue/article.pdffoo", False),
            # Article citation ENW.
            ("/fr/revues/journal/2020-issue/article/citation.enw", "article_citation_enw"),
            ("/fr/revues/journal/2020-issue/article.enw", "article_enw"),
            ("/fr/revues/journal/2020-issue/article/foo.enw", False),
            ("/fr/revues/journal/2020-issue/article.enwfoo", False),
            # Article citation RIS.
            ("/fr/revues/journal/2020-issue/article/citation.ris", "article_citation_ris"),
            ("/fr/revues/journal/2020-issue/article.ris", "article_ris"),
            ("/fr/revues/journal/2020-issue/article/foo.ris", False),
            ("/fr/revues/journal/2020-issue/article.risfoo", False),
            # Article citation BIB.
            ("/fr/revues/journal/2020-issue/article/citation.bib", "article_citation_bib"),
            ("/fr/revues/journal/2020-issue/article.bib", "article_bib"),
            ("/fr/revues/journal/2020-issue/article/foo.bib", False),
            ("/fr/revues/journal/2020-issue/article.bibfoo", False),
        ],
    )
    def test_article_url_patterns(self, url, expected_url_name):
        if expected_url_name:
            resolver = resolve(url)
            assert resolver.url_name == expected_url_name
        else:
            with pytest.raises(Resolver404):
                resolver = resolve(url)
