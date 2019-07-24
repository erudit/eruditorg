import pytest

from bs4 import BeautifulSoup
from django.test import Client
from django.urls import reverse

from erudit.test.factories import ArticleFactory, SolrDocumentFactory


@pytest.mark.django_db
class TestSearchResultsView:

    def test_search_results_citation_modal(self, solr_client):
        # Article in Fedora, citation tools should be displayed.
        ArticleFactory(localidentifier='foo', title='foo')
        # Search result not in Fedora, citation tools should not be displayed.
        doc = SolrDocumentFactory(id='bar', title='foo bar')
        solr_client.add_document(doc)

        url = reverse('public:search:results')
        response = Client().get(url, data={'basic_search_term': 'foo'})
        html = response.content.decode()
        dom = BeautifulSoup(html, 'html.parser')
        results = dom.find('ol', {'class': 'results'})

        # There should be two search results.
        assert len(results.find_all('li', {'class': 'result'})) == 2
        # The search result which is in fedora should display the citation tools.
        assert 'Citer cet article' in results.find('a', {'data-modal-id': '#id_cite_modal_foo'}).text
        # The search result which is not in fedora should not display the citation tools.
        assert results.find('a', {'data-modal-id': '#id_cite_modal_bar'}) is None

    def test_search_results_citation_modal_is_the_same_as_the_article_detail(self):
        article = ArticleFactory(localidentifier='foo', title='foo')

        url = reverse('public:search:results')
        response = Client().get(url, data={'basic_search_term': 'foo'})
        html = response.content.decode()
        dom = BeautifulSoup(html, 'html.parser')
        search_result_citation_tools = dom.find('div', {'id': 'id_cite_modal_foo'})

        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        response = Client().get(url, data={'basic_search_term': 'foo'})
        html = response.content.decode()
        dom = BeautifulSoup(html, 'html.parser')
        article_detail_citation_tools = dom.find('div', {'id': 'id_cite_modal_foo'})

        assert search_result_citation_tools == article_detail_citation_tools
