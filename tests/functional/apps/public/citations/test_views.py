# -*- coding: utf-8 -*-

import json
import mock

from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.urlresolvers import reverse
from django.test.utils import override_settings
from django.utils.encoding import force_text
import pytest

from base.test.testcases import EruditClientTestCase
from core.citations.middleware import SavedCitationListMiddleware
from core.citations.models import SavedCitationList
from core.citations.test.factories import SavedCitationListFactory

from erudit.test.factories import ArticleFactory
from erudit.test.factories import AuthorFactory
from erudit.test.factories import CollectionFactory
from erudit.test.factories import IssueFactory
from erudit.test.factories import JournalFactory
from erudit.test.factories import ThesisFactory
from erudit.fedora.modelmixins import FedoraMixin

from apps.public.citations.views import SavedCitationAddView
from apps.public.citations.views import SavedCitationRemoveView


class TestSavedCitationListView(EruditClientTestCase):

    @pytest.fixture(autouse=True)
    def setup(self):
        author_1 = AuthorFactory.create(lastname='Abc', firstname='Def')
        author_2 = AuthorFactory.create(lastname='Def', firstname='ghi')
        self.collection_1 = CollectionFactory.create()
        self.thesis_1 = ThesisFactory.create(
            localidentifier='t1', collection=self.collection_1, author=author_1, title='Thesis A',
            publication_year=2014)
        self.thesis_2 = ThesisFactory.create(
            localidentifier='t2', collection=self.collection_1, author=author_2, title='Thesis B',
            publication_year=2011)
        author_3 = AuthorFactory.create(lastname='Ghi', firstname='Jkl')
        author_4 = AuthorFactory.create(lastname='Jkl', firstname='mno')
        self.journal_1 = JournalFactory.create(
            collection=self.collection, type_code='S')
        self.journal_2 = JournalFactory.create(
            collection=self.collection, type_code='C')
        self.issue_1 = IssueFactory.create(journal=self.journal_1, year=2012)
        self.issue_2 = IssueFactory.create(journal=self.journal_2, year=2013)
        self.article_1 = ArticleFactory.create(issue=self.issue_1)
        self.article_2 = ArticleFactory.create(issue=self.issue_1)
        self.article_3 = ArticleFactory.create(issue=self.issue_2)
        self.article_1.authors.add(author_3)
        self.article_2.authors.add(author_4)
        self.article_3.authors.add(author_3)
        clist = SavedCitationListFactory.create(user=self.user)
        clist.documents.add(self.thesis_1)
        clist.documents.add(self.thesis_2)
        clist.documents.add(self.article_1)
        clist.documents.add(self.article_2)
        clist.documents.add(self.article_3)

    def get_mocked_erudit_object(self):
        m = mock.MagicMock()
        m.get_formatted_title.return_value = "mocked title"
        return m

    @override_settings(DEBUG=True)
    @mock.patch.object(FedoraMixin, 'get_erudit_object')
    def test_embeds_the_count_of_scientific_articles_in_the_context(self, mock_erudit_object):

        # Setup
        mock_erudit_object.return_value = self.get_mocked_erudit_object()
        self.client.login(username='foo', password='notreallysecret')
        url = reverse('public:citations:list')
        # Run
        response = self.client.get(url)
        # Check
        assert response.status_code == 200
        assert response.context['scientific_articles_count'] == 2

    @mock.patch.object(FedoraMixin, 'get_erudit_object')
    def test_embeds_the_count_of_cultural_articles_in_the_context(self, mock_erudit_object):

        # Setup
        mock_erudit_object.return_value = self.get_mocked_erudit_object()
        self.client.login(username='foo', password='notreallysecret')
        url = reverse('public:citations:list')
        # Run
        response = self.client.get(url)
        # Check
        assert response.status_code == 200
        assert response.context['cultural_articles_count'] == 1

    @mock.patch.object(FedoraMixin, 'get_erudit_object')
    def test_embeds_the_count_of_theses_in_the_context(self, mock_erudit_object):
        # Setup
        mock_erudit_object.return_value = self.get_mocked_erudit_object()
        self.client.login(username='foo', password='notreallysecret')
        url = reverse('public:citations:list')
        # Run
        response = self.client.get(url)
        # Check
        assert response.status_code == 200
        assert response.context['theses_count'] == 2

    @mock.patch.object(FedoraMixin, 'get_erudit_object')
    def test_can_sort_documents_by_ascending_title(self, mock_erudit_object):
        # Setup
        mock_erudit_object.return_value = self.get_mocked_erudit_object()
        self.client.login(username='foo', password='notreallysecret')
        url = reverse('public:citations:list')
        # Run
        response = self.client.get(url, data={'sort_by': 'title_asc'})
        # Check
        assert response.status_code == 200
        assert list(response.context['documents']) == [
            self.thesis_1, self.thesis_2, self.article_1, self.article_2, self.article_3, ]

    @mock.patch.object(FedoraMixin, 'get_erudit_object')
    def test_can_sort_documents_by_descending_title(self, mock_erudit_object):
        # Setup
        mock_erudit_object.return_value = self.get_mocked_erudit_object()
        self.client.login(username='foo', password='notreallysecret')
        url = reverse('public:citations:list')
        # Run
        response = self.client.get(url, data={'sort_by': 'title_desc'})
        # Check
        assert response.status_code == 200
        assert list(response.context['documents']) == [
            self.article_1, self.article_2, self.article_3, self.thesis_2, self.thesis_1, ]

    @mock.patch.object(FedoraMixin, 'get_erudit_object')
    def test_can_sort_documents_by_ascending_year(self, mock_erudit_object):
        # Setup
        mock_erudit_object.return_value = self.get_mocked_erudit_object()
        self.client.login(username='foo', password='notreallysecret')
        url = reverse('public:citations:list')
        # Run
        response = self.client.get(url, data={'sort_by': 'year_asc'})
        # Check
        assert response.status_code == 200
        assert list(response.context['documents']) == [
            self.thesis_2, self.article_1, self.article_2, self.article_3, self.thesis_1, ]

    @mock.patch.object(FedoraMixin, 'get_erudit_object')
    def test_can_sort_documents_by_descending_year(self, mock_erudit_object):
        # Setup
        mock_erudit_object.return_value = self.get_mocked_erudit_object()
        self.client.login(username='foo', password='notreallysecret')
        url = reverse('public:citations:list')
        # Run
        response = self.client.get(url, data={'sort_by': 'year_desc'})
        # Check
        assert response.status_code == 200
        assert list(response.context['documents']) == [
            self.thesis_1, self.article_3, self.article_1, self.article_2, self.thesis_2, ]

    @mock.patch.object(FedoraMixin, 'get_erudit_object')
    def test_can_sort_documents_by_ascending_author_name(self, mock_erudit_object):
        # Setup
        mock_erudit_object.return_value = self.get_mocked_erudit_object()
        self.client.login(username='foo', password='notreallysecret')
        url = reverse('public:citations:list')
        # Run
        response = self.client.get(url, data={'sort_by': 'author_asc'})
        # Check
        assert response.status_code == 200
        assert list(response.context['documents']) == [
            self.thesis_1, self.thesis_2, self.article_1, self.article_3, self.article_2, ]

    @mock.patch.object(FedoraMixin, 'get_erudit_object')
    def test_can_sort_documents_by_descending_author_name(self, mock_erudit_object):
        # Setup
        mock_erudit_object.return_value = self.get_mocked_erudit_object()
        self.client.login(username='foo', password='notreallysecret')
        url = reverse('public:citations:list')
        # Run
        response = self.client.get(url, data={'sort_by': 'author_desc'})
        # Check
        assert response.status_code == 200
        assert list(response.context['documents']) == [
            self.article_2, self.article_1, self.article_3, self.thesis_2, self.thesis_1, ]


class TestSavedCitationAddView(EruditClientTestCase):
    def test_can_add_an_article_to_a_citation_list(self):
        # Setup
        issue = IssueFactory.create(journal=self.journal)
        article = ArticleFactory.create(issue=issue)
        request = self.factory.post('/')
        request.user = AnonymousUser()
        SessionMiddleware().process_request(request)
        SavedCitationListMiddleware().process_request(request)
        view = SavedCitationAddView.as_view()
        # Run
        response = view(request, article.id)
        # Check
        assert response.status_code == 200
        assert list(request.saved_citations) == [str(article.id), ]


class TestSavedCitationRemoveView(EruditClientTestCase):
    def test_can_remove_an_article_from_a_citation_list(self):
        # Setup
        issue = IssueFactory.create(journal=self.journal)
        article = ArticleFactory.create(issue=issue)
        request = self.factory.post('/')
        request.user = AnonymousUser()
        SessionMiddleware().process_request(request)
        SavedCitationListMiddleware().process_request(request)
        request.saved_citations.add(article)
        view = SavedCitationRemoveView.as_view()
        # Run
        response = view(request, article.id)
        # Check
        assert response.status_code == 200
        assert not len(request.saved_citations)

    def test_can_properly_handle_the_case_where_an_item_is_no_longer_in_the_citation_list(self):
        # Setup
        issue = IssueFactory.create(journal=self.journal)
        article = ArticleFactory.create(issue=issue)
        request = self.factory.post('/')
        request.user = AnonymousUser()
        SessionMiddleware().process_request(request)
        SavedCitationListMiddleware().process_request(request)
        view = SavedCitationRemoveView.as_view()
        # Run
        response = view(request, article.id)
        # Check
        assert response.status_code == 200
        assert 'error' in json.loads(force_text(response.content))


class TestSavedCitationBatchRemoveView(EruditClientTestCase):
    @pytest.fixture(autouse=True)
    def setup(self):
        author_1 = AuthorFactory.create(lastname='Abc', firstname='Def')
        author_2 = AuthorFactory.create(lastname='Def', firstname='ghi')
        self.collection_1 = CollectionFactory.create()
        self.thesis_1 = ThesisFactory.create(
            localidentifier='t1', collection=self.collection_1, author=author_1, title='Thesis A',
            publication_year=2014)
        self.thesis_2 = ThesisFactory.create(
            localidentifier='t2', collection=self.collection_1, author=author_2, title='Thesis B',
            publication_year=2011)
        author_3 = AuthorFactory.create(lastname='Ghi', firstname='Jkl')
        author_4 = AuthorFactory.create(lastname='Jkl', firstname='mno')
        self.journal_1 = JournalFactory.create(
            collection=self.collection, type_code='S')
        self.journal_2 = JournalFactory.create(
            collection=self.collection, type_code='C')
        self.issue_1 = IssueFactory.create(journal=self.journal_1, year=2012)
        self.issue_2 = IssueFactory.create(journal=self.journal_2, year=2013)
        self.article_1 = ArticleFactory.create(issue=self.issue_1)
        self.article_2 = ArticleFactory.create(issue=self.issue_1)
        self.article_3 = ArticleFactory.create(issue=self.issue_2)
        self.article_1.authors.add(author_3)
        self.article_2.authors.add(author_4)
        self.article_3.authors.add(author_3)
        clist = SavedCitationListFactory.create(user=self.user)
        clist.documents.add(self.thesis_1)
        clist.documents.add(self.thesis_2)
        clist.documents.add(self.article_1)
        clist.documents.add(self.article_2)
        clist.documents.add(self.article_3)

    def test_can_remove_many_documents_from_a_saved_citations_list(self):
        # Setup
        self.client.login(username='foo', password='notreallysecret')
        url = reverse('public:citations:remove_citation_batch')
        # Run
        response = self.client.post(
            url, data={'document_ids': [self.thesis_1.id, self.article_1.id, ]})
        # Check
        assert response.status_code == 200
        clist = SavedCitationList.objects.get(user=self.user)
        assert not clist.documents.filter(id__in=[self.thesis_1.id, self.article_1.id, ]).exists()

    def test_cannot_handle_an_empty_list_of_document_ids(self):
        # Setup
        self.client.login(username='foo', password='notreallysecret')
        url = reverse('public:citations:remove_citation_batch')
        # Run
        response = self.client.post(url, data={'document_ids': []})
        # Check
        assert response.status_code == 404

    def test_cannot_handle_a_list_of_document_ids_containing_incorrect_values(self):
        # Setup
        self.client.login(username='foo', password='notreallysecret')
        url = reverse('public:citations:remove_citation_batch')
        # Run
        response = self.client.post(url, data={'document_ids': ['foo', 'bar', ]})
        # Check
        assert response.status_code == 404


class TestBaseEruditDocumentsCitationView(EruditClientTestCase):
    @pytest.fixture(autouse=True)
    def setup(self):
        author_1 = AuthorFactory.create(lastname='Abc', firstname='Def')
        author_2 = AuthorFactory.create(lastname='Def', firstname='ghi')
        self.collection_1 = CollectionFactory.create()
        self.thesis_1 = ThesisFactory.create(
            localidentifier='t1', collection=self.collection_1, author=author_1, title='Thesis A',
            publication_year=2014)
        self.thesis_2 = ThesisFactory.create(
            localidentifier='t2', collection=self.collection_1, author=author_2, title='Thesis B',
            publication_year=2011)
        author_3 = AuthorFactory.create(lastname='Ghi', firstname='Jkl')
        author_4 = AuthorFactory.create(lastname='Jkl', firstname='mno')
        self.journal_1 = JournalFactory.create(
            collection=self.collection, type_code='S')
        self.journal_2 = JournalFactory.create(
            collection=self.collection, type_code='C')
        self.issue_1 = IssueFactory.create(journal=self.journal_1, year=2012)
        self.issue_2 = IssueFactory.create(journal=self.journal_2, year=2013)
        self.article_1 = ArticleFactory.create(issue=self.issue_1)
        self.article_2 = ArticleFactory.create(issue=self.issue_1)
        self.article_3 = ArticleFactory.create(issue=self.issue_2)
        self.article_1.authors.add(author_3)
        self.article_2.authors.add(author_4)
        self.article_3.authors.add(author_3)
        clist = SavedCitationListFactory.create(user=self.user)
        clist.documents.add(self.thesis_1)
        clist.documents.add(self.thesis_2)
        clist.documents.add(self.article_1)
        clist.documents.add(self.article_2)
        clist.documents.add(self.article_3)

    def test_can_generate_an_export_for_multiple_documents(self):
        # Setup
        self.client.login(username='foo', password='notreallysecret')
        url = reverse('public:citations:citation_enw')
        # Run
        response = self.client.get(
            url, data={'document_ids': [self.thesis_1.id, self.article_1.id, ]})
        # Check
        assert response.status_code == 200

    def test_cannot_generate_an_export_for_an_empty_list_of_document_ids(self):
        # Setup
        self.client.login(username='foo', password='notreallysecret')
        url = reverse('public:citations:citation_enw')
        # Run
        response = self.client.get(url, data={'document_ids': []})
        # Check
        assert response.status_code == 404

    def test_cannot_generate_an_export_for_a_list_of_document_ids_containing_incorrect_values(self):
        # Setup
        self.client.login(username='foo', password='notreallysecret')
        url = reverse('public:citations:citation_enw')
        # Run
        response = self.client.get(url, data={'document_ids': ['foo', 'bar', ]})
        # Check
        assert response.status_code == 404
