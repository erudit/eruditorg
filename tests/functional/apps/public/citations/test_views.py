import json

from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.urlresolvers import reverse
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

from apps.public.citations.views import SavedCitationAddView
from apps.public.citations.views import SavedCitationRemoveView

pytestmark = pytest.mark.usefixtures('patch_erudit_article')

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

    def test_embeds_the_count_of_article_types_in_the_context(self):
        self.client.login(username='foo', password='notreallysecret')
        url = reverse('public:citations:list')
        response = self.client.get(url)
        assert response.status_code == 200
        assert response.context['scientific_articles_count'] == 2
        assert response.context['cultural_articles_count'] == 1
        assert response.context['theses_count'] == 2

    @pytest.mark.parametrize('criteria,expected_order', [
        ('title_asc', ['a1', 'a2', 'a3', 't1', 't2']),
        ('title_desc', ['t2', 't1', 'a1', 'a2', 'a3']),
        ('year_asc', ['t2', 'a1', 'a2', 'a3', 't1']),
        ('year_desc', ['t1', 'a3', 'a1', 'a2', 't2']),
        ('author_asc', ['t1', 't2', 'a1', 'a3', 'a2']),
        ('author_desc', ['a2', 'a1', 'a3', 't2', 't1']),
    ])
    def test_can_sort_documents_by_criteria(self, criteria, expected_order):
        MAP = {
            self.article_1: 'a1',
            self.article_2: 'a2',
            self.article_3: 'a3',
            self.thesis_1: 't1',
            self.thesis_2: 't2',
        }

        self.client.login(username='foo', password='notreallysecret')
        url = reverse('public:citations:list')
        response = self.client.get(url, data={'sort_by': criteria})
        documents = list(response.context['documents'])
        ordered_ids = [MAP[doc] for doc in documents]

        assert response.status_code == 200
        assert ordered_ids == expected_order


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
