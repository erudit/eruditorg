import json

from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.urls import reverse
from django.utils.encoding import force_str
from django.test import RequestFactory
import pytest

from base.test.testcases import Client
from base.test.factories import UserFactory
from core.citations.middleware import SavedCitationListMiddleware
from erudit.fedora import repository

from erudit.test import needs_fr_ca
from erudit.test.factories import ArticleFactory
from erudit.test.factories import CollectionFactory
from erudit.test.factories import IssueFactory
from erudit.test.factories import JournalFactory
from erudit.test.factories import ThesisFactory
from erudit.test.factories import SolrDocumentFactory

from apps.public.citations.views import SavedCitationAddView
from apps.public.citations.views import SavedCitationRemoveView


pytestmark = pytest.mark.django_db


class TestSavedCitationListView:

    @pytest.fixture(autouse=True)
    def setup(self, solr_client):
        self.collection = CollectionFactory.create(
            code='erudit', localidentifier='erudit', name='Érudit')
        self.collection_1 = CollectionFactory.create()
        self.thesis_1 = ThesisFactory.create(
            id='t1', authors=['Abc, Def'], title='Thesis A', year=2014)
        solr_client.add_document(self.thesis_1)
        self.thesis_2 = ThesisFactory.create(
            id='t2', authors=['Def, ghi'], title='Thesis B', year=2011)
        solr_client.add_document(self.thesis_2)
        self.journal_1 = JournalFactory.create(
            collection=self.collection, type_code='S')
        self.journal_2 = JournalFactory.create(
            collection=self.collection, type_code='C')
        self.issue_1 = IssueFactory.create(journal=self.journal_1, year=2012)
        self.issue_2 = IssueFactory.create(journal=self.journal_2, year=2013)
        self.article_1 = ArticleFactory.create(issue=self.issue_1, localidentifier='a1')
        self.article_2 = ArticleFactory.create(issue=self.issue_1, localidentifier='a2')
        self.article_3 = ArticleFactory.create(issue=self.issue_2, localidentifier='a3')
        with repository.api.open_article(self.article_1.get_full_identifier()) as wrapper:
            wrapper.set_title("Article 1")
            wrapper.set_author(lastname='Ghi', firstname='Jlk')
        solr_client.add_article(self.article_1)
        with repository.api.open_article(self.article_2.get_full_identifier()) as wrapper:
            wrapper.set_title("Article 2")
            wrapper.set_author(lastname='Jlk', firstname='mno')
        solr_client.add_article(self.article_2)
        with repository.api.open_article(self.article_3.get_full_identifier()) as wrapper:
            wrapper.set_title("Article 3")
            wrapper.set_author(lastname='Ghi', firstname='Jlk')
        solr_client.add_article(self.article_3)
        self.user = UserFactory()
        self.user.saved_citations.create(solr_id=self.thesis_1.id)
        self.user.saved_citations.create(solr_id=self.thesis_2.id)
        self.user.saved_citations.create(solr_id=self.article_1.localidentifier)
        self.user.saved_citations.create(solr_id=self.article_2.localidentifier)
        self.user.saved_citations.create(solr_id=self.article_3.localidentifier)
        self.client = Client(logged_user=self.user)

    def test_embeds_the_count_of_article_types_in_the_context(self):
        url = reverse('public:citations:list')
        response = self.client.get(url)
        assert response.status_code == 200
        assert response.context['scientific_articles_count'] == 2
        assert response.context['cultural_articles_count'] == 1
        assert response.context['theses_count'] == 2

    # needs fr_ca locale to properly sort authors
    @needs_fr_ca
    @pytest.mark.parametrize('criteria,expected_order', [
        ('title_asc', ['a1', 'a2', 'a3', 't1', 't2']),
        ('title_desc', ['t2', 't1', 'a3', 'a2', 'a1']),
        ('year_asc', ['t2', 'a1', 'a2', 'a3', 't1']),
        ('year_desc', ['t1', 'a3', 'a2', 'a1', 't2']),
        ('author_asc', ['t1', 't2', 'a1', 'a3', 'a2']),
        ('author_desc', ['a2', 'a3', 'a1', 't2', 't1']),
    ])
    def test_can_sort_documents_by_criteria(self, criteria, expected_order):
        url = reverse('public:citations:list')
        response = self.client.get(url, data={'sort_by': criteria})
        documents = list(response.context['documents'])
        ordered_ids = [doc.localidentifier for doc in documents]

        assert response.status_code == 200
        assert ordered_ids == expected_order
        assert b'Ghi' in response.content
        assert b'Jlk' in response.content

    def test_can_generate_an_export_for_multiple_documents(self):
        url = reverse('public:citations:citation_enw')
        response = self.client.get(
            url, data={'document_ids': [
                self.thesis_1.id, self.article_1.localidentifier
            ]}
        )
        assert response.status_code == 200

    def test_cannot_generate_an_export_for_an_empty_list_of_document_ids(self):
        url = reverse('public:citations:citation_enw')
        response = self.client.get(url, data={'document_ids': []})
        assert response.status_code == 404

    def test_cannot_generate_an_export_for_a_list_of_document_ids_containing_incorrect_values(self):
        url = reverse('public:citations:citation_enw')
        response = self.client.get(url, data={'document_ids': ['foo', 'bar', ]})
        assert response.status_code == 404


def test_cannot_cite_article_not_in_fedora(solr_client):
    doc = SolrDocumentFactory()
    solr_client.add_document(doc)
    user = UserFactory()
    user.saved_citations.create(solr_id=doc.id)
    client = Client(logged_user=user)
    url = reverse('public:citations:list')
    response = client.get(url)
    assert b'data-document-id' in response.content
    assert b'id_cite_modal_' not in response.content


class TestSavedCitationAddView:

    def test_cannot_cite_article_not_in_fedora(self, solr_client):
        doc = SolrDocumentFactory()
        solr_client.add_document(doc)
        user = UserFactory()
        user.saved_citations.create(solr_id=doc.id)
        client = Client(logged_user=user)
        url = reverse('public:citations:list')
        response = client.get(url)
        assert b'data-document-id' in response.content
        assert b'id_cite_modal_' not in response.content

    def test_can_add_an_article_to_a_citation_list(self):
        issue = IssueFactory.create()
        article = ArticleFactory.create(issue=issue)
        request = RequestFactory().post('/', data={'document_id': article.localidentifier})
        request.user = AnonymousUser()
        SessionMiddleware().process_request(request)
        SavedCitationListMiddleware().process_request(request)
        view = SavedCitationAddView.as_view()
        response = view(request)
        assert response.status_code == 200
        assert list(request.saved_citations) == [str(article.localidentifier), ]


class TestSavedCitationRemoveView:
    def test_can_remove_an_article_from_a_citation_list(self):
        # Setup
        issue = IssueFactory.create()
        article = ArticleFactory.create(issue=issue)
        request = RequestFactory().post('/', data={'document_id': article.localidentifier})
        request.user = AnonymousUser()
        SessionMiddleware().process_request(request)
        SavedCitationListMiddleware().process_request(request)
        request.saved_citations.add(article.localidentifier)
        view = SavedCitationRemoveView.as_view()
        response = view(request)
        assert response.status_code == 200
        assert not len(request.saved_citations)

    def test_can_properly_handle_the_case_where_an_item_is_no_longer_in_the_citation_list(self):
        issue = IssueFactory.create()
        article = ArticleFactory.create(issue=issue)
        request = RequestFactory().post('/', data={'document_id': article.localidentifier})
        request.user = AnonymousUser()
        SessionMiddleware().process_request(request)
        SavedCitationListMiddleware().process_request(request)
        view = SavedCitationRemoveView.as_view()
        response = view(request)
        assert response.status_code == 200
        assert 'error' in json.loads(force_str(response.content))


class TestSavedCitationBatchRemoveView:
    @pytest.fixture(autouse=True)
    def setup(self, solr_client):
        self.thesis_1 = ThesisFactory.create(
            id='t1', authors=['Abc, Def'], title='Thesis A', year=2014)
        solr_client.add_document(self.thesis_1)
        self.thesis_2 = ThesisFactory.create(
            id='t2', authors=['Def, ghi'], title='Thesis B', year=2011)
        solr_client.add_document(self.thesis_2)
        self.journal_1 = JournalFactory.create(type_code='S')
        self.journal_2 = JournalFactory.create(type_code='C')
        self.issue_1 = IssueFactory.create(journal=self.journal_1, year=2012)
        self.issue_2 = IssueFactory.create(journal=self.journal_2, year=2013)
        self.article_1 = ArticleFactory.create(issue=self.issue_1)
        solr_client.add_article(self.article_1)
        self.article_2 = ArticleFactory.create(issue=self.issue_1)
        solr_client.add_article(self.article_2)
        self.article_3 = ArticleFactory.create(issue=self.issue_2)
        solr_client.add_article(self.article_3)
        with repository.api.open_article(self.article_1.get_full_identifier()) as wrapper:
            wrapper.set_author(lastname='Ghi', firstname='Jlk')
        with repository.api.open_article(self.article_2.get_full_identifier()) as wrapper:
            wrapper.set_author(lastname='Jlk', firstname='mno')
        with repository.api.open_article(self.article_3.get_full_identifier()) as wrapper:
            wrapper.set_author(lastname='Ghi', firstname='Jlk')
        self.user = UserFactory()
        self.user.saved_citations.create(solr_id=self.thesis_1.id)
        self.user.saved_citations.create(solr_id=self.thesis_2.id)
        self.user.saved_citations.create(solr_id=self.article_1.localidentifier)
        self.user.saved_citations.create(solr_id=self.article_2.localidentifier)
        self.user.saved_citations.create(solr_id=self.article_3.localidentifier)
        self.client = Client(logged_user=self.user)

    def test_can_remove_many_documents_from_a_saved_citations_list(self):
        url = reverse('public:citations:remove_citation_batch')
        idlist = [
            self.thesis_1.id,
            self.article_1.localidentifier,
        ]
        response = self.client.post(url, data={'document_ids': idlist})
        assert response.status_code == 200
        assert not self.user.saved_citations.filter(solr_id__in=idlist).exists()

    def test_cannot_handle_an_empty_list_of_document_ids(self):
        url = reverse('public:citations:remove_citation_batch')
        response = self.client.post(url, data={'document_ids': []})
        assert response.status_code == 404

    def test_cannot_handle_a_list_of_document_ids_containing_incorrect_values(self):
        url = reverse('public:citations:remove_citation_batch')
        response = self.client.post(url, data={'document_ids': ['foo', 'bar', ]})
        assert response.status_code == 404
