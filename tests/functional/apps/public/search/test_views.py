import json
import unittest.mock
from faker import Faker

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.urlresolvers import reverse
from django.test import RequestFactory
from django.test.utils import override_settings
from django.utils.encoding import smart_text
from django.utils.timezone import now
import pytest

from core.solrq.query import Query
from erudit.test import BaseEruditTestCase
from erudit.test.factories import ArticleFactory
from erudit.test.factories import IssueFactory
from erudit.models import Article

from apps.public.search.saved_searches import SavedSearchList
from apps.public.search.views import AdvancedSearchView
from apps.public.search.views import EruditDocumentListAPIView
from apps.public.search.views import SavedSearchAddView
from apps.public.search.views import SavedSearchRemoveView
from apps.public.search.views import instantiate_real_object


pytestmark = pytest.mark.django_db

faker = Faker()


def fake_get_results(**kwargs):
    results = unittest.mock.Mock()
    results.docs = [
        {'ID': a.localidentifier, 'Corpus_fac': 'Article'} for a in Article.objects.all()
    ]
    results.facets = {
        'facet_fields': {
            'Annee': ['1995', 12, '1996', 12, ],
            'TypeArticle_fac': ['Article', 12, 'Culturel', 12],
            'Langue': ['fr', 12, 'en', 12],
            'TitreCollection_fac': ['Article', 12, 'Livre', 12],
            'Auteur_tri': ['author 1', 12, 'author 2', 12],
            'Fonds_fac': ['Erudit', 12, 'Erudit 2', 12],
            'Corpus_fac': ['val1', 12, 'val2', 14, ],
        }
    }
    results.hits = 50
    return results


def fake_get_results_external(**kwargs):
    results = unittest.mock.Mock()
    results.docs = [
        {
            'ID': 'depot-{}'.format(id),
            'AuteurNP_fac': [faker.name() for i in range(3)],
            'URLDocument': [faker.uri()],
            'Annee': [faker.year()],
            'Corpus_fac': 'Dépot',
        }
        for id in range(50)
    ]
    results.facets = {'facet_fields': {'Corpus_fac': ['val1', 12, 'val2', 14, ], }}
    results.hits = 50
    return results


class TestEruditDocumentListAPIView:
    @unittest.mock.patch.object(Query, 'get_results')
    def test_can_return_erudit_documents(self, mock_get_results):
        # Setup
        mock_get_results.side_effect = fake_get_results
        issue = IssueFactory.create(date_published=now())
        localidentifiers = []
        for i in range(0, 50):
            lid = 'lid-{0}'.format(i)
            localidentifiers.append(lid)
            ArticleFactory.create(issue=issue, localidentifier=lid)

        request = RequestFactory().get('/', data={'format': 'json'})
        list_view = EruditDocumentListAPIView.as_view()

        # Run
        results_data = list_view(request).render().content
        # Check
        results = json.loads(smart_text(results_data))
        assert results['pagination']['count'] == 50

    @unittest.mock.patch.object(Query, 'get_results')
    def test_can_return_erudit_documents_not_in_fedora(self, mock_get_results):
        # Setup
        mock_get_results.side_effect = fake_get_results
        issue = IssueFactory.create(date_published=now())
        localidentifiers = []
        for i in range(0, 1):
            lid = 'lid-{0}'.format(i)
            localidentifiers.append(lid)
            ArticleFactory.create(issue=issue, localidentifier=lid)

        request = RequestFactory().get('/', data={'format': 'json'})
        list_view = EruditDocumentListAPIView.as_view()

        # Run
        results_data = list_view(request).render().content
        # Check
        results = json.loads(smart_text(results_data))
        assert results['pagination']['count'] == 50

    @unittest.mock.patch.object(Query, 'get_results')
    def test_can_return_erudit_documents_not_in_database(self, mock_get_results):
        # Setup
        mock_get_results.side_effect = fake_get_results_external
        request = RequestFactory().get('/', data={'format': 'json'})
        list_view = EruditDocumentListAPIView.as_view()

        # Run
        results_data = list_view(request).render().content
        # Check
        results = json.loads(smart_text(results_data))
        assert results['pagination']['count'] == 50

    # This NO_CACHES override is needed because otherwise the cache.set() call tries to picke our
    # mock erudit object and crashes.
    @override_settings(CACHES=settings.NO_CACHES)
    @unittest.mock.patch.object(Query, 'get_results')
    def test_fedora_issue_with_external_url_yield_no_pdf_link(self, mock_get_results):
        # When an fedora issue has an external_url (for example, RECMA. see #1651), we don't want
        # any of its articles to yield a PDF link.
        mock_get_results.side_effect = fake_get_results
        issue = IssueFactory.create(external_url='http://www.example.com')
        ArticleFactory.create(issue=issue, localidentifier='foo')

        request = RequestFactory().get('/', data={'format': 'json'})
        list_view = EruditDocumentListAPIView.as_view()

        results_data = list_view(request).render().content
        results = json.loads(smart_text(results_data))

        obj = results['results'][0]
        instantiate_real_object(obj)
        assert obj['real_object'].pdf_url is None


class TestAdvancedSearchView:
    def test_can_insert_the_saved_searches_into_the_context(self):
        # Setup
        url = reverse('public:search:advanced_search')
        request = RequestFactory().get(url)
        request.user = AnonymousUser()
        SessionMiddleware().process_request(request)
        view = AdvancedSearchView.as_view()
        searches = SavedSearchList(request)
        searches.add('foo=bar&xyz=test', 100)
        searches.save()
        # Run
        response = view(request)
        # Check
        assert response.status_code == 200
        assert len(response.context_data['saved_searches']) == 1
        assert response.context_data['saved_searches'][0]['querystring'] \
            == searches[0]['querystring']
        assert response.context_data['saved_searches'][0]['results_count'] == 100


class TestSearchResultsView(BaseEruditTestCase):
    def test_redirects_to_the_advanced_search_form_if_no_parameters_are_present(self):
        # Setup
        url = reverse('public:search:results')
        # Run
        response = self.client.get(url, follow=True)
        # Check
        self.assertTrue(len(response.redirect_chain))
        last_url, status_code = response.redirect_chain[-1]
        self.assertTrue(reverse('public:search:advanced_search') in last_url)

    @unittest.mock.patch.object(Query, 'get_results')
    def test_redirects_to_the_advanced_search_form_if_the_search_api_does_not_return_a_200(self, mock_get_results):  # noqa
        url = reverse('public:search:results')
        # Run
        mock_get_results.side_effect = fake_get_results
        response = self.client.get(url, follow=True, data={'basic_search_term': 'poulet', 'page': '6'})

        assert len(response.redirect_chain) == 1
        last_url, status_code = response.redirect_chain[-1]
        assert reverse('public:search:advanced_search') in last_url




class TestSavedSearchAddView:
    def test_can_add_a_search_to_the_list_of_saved_searches(self):
        # Setup
        request = RequestFactory().post('/', {'querystring': 'foo=bar&xyz=test', 'results_count': 100})
        request.user = AnonymousUser()
        SessionMiddleware().process_request(request)
        view = SavedSearchAddView.as_view()
        # Run
        response = view(request)
        # Check
        assert response.status_code == 200
        searches = SavedSearchList(request)
        assert len(searches) == 1
        assert searches[0]['querystring'] == 'foo=bar&xyz=test'
        assert searches[0]['results_count'] == 100
        assert searches[0]['uuid']
        assert searches[0]['timestamp']

    def test_cannot_add_a_search_if_the_querystring_is_not_provided(self):
        # Setup
        request = RequestFactory().post('/', {'results_count': 100})
        request.user = AnonymousUser()
        SessionMiddleware().process_request(request)
        view = SavedSearchAddView.as_view()
        # Run
        view(request)
        # Check
        searches = SavedSearchList(request)
        assert not len(searches)

    def test_cannot_add_a_search_if_the_results_count_is_not_provided(self):
        # Setup
        request = RequestFactory().post('/', {'querystring': 'foo=bar&xyz=test'})
        request.user = AnonymousUser()
        SessionMiddleware().process_request(request)
        view = SavedSearchAddView.as_view()
        # Run
        view(request)
        # Check
        searches = SavedSearchList(request)
        assert not len(searches)

    def test_cannot_add_a_search_if_the_querystring_is_not_a_valid_querystring(self):
        # Setup
        request = RequestFactory().post('/', {'querystring': 'bad', 'results_count': 100})
        request.user = AnonymousUser()
        SessionMiddleware().process_request(request)
        view = SavedSearchAddView.as_view()
        # Run
        view(request)
        # Check
        searches = SavedSearchList(request)
        assert not len(searches)

    def test_cannot_add_a_search_if_the_results_count_is_not_an_integer(self):
        # Setup
        request = RequestFactory().post(
            '/', {'querystring': 'foo=bar&xyz=test', 'results_count': 'bad'})
        request.user = AnonymousUser()
        SessionMiddleware().process_request(request)
        view = SavedSearchAddView.as_view()
        # Run
        view(request)
        # Check
        searches = SavedSearchList(request)
        assert not len(searches)


class TestSavedSearchRemoveView:
    def test_can_remove_a_search_from_the_list_of_saved_searches(self):
        # Setup
        request = RequestFactory().post('/')
        request.user = AnonymousUser()
        SessionMiddleware().process_request(request)
        view = SavedSearchRemoveView.as_view()
        searches = SavedSearchList(request)
        searches.add('foo=bar&xyz=test', 100)
        searches.save()
        uuid = searches[0]['uuid']
        # Run
        response = view(request, uuid)
        # Check
        assert response.status_code == 200
        searches = SavedSearchList(request)
        assert not len(searches)

    def test_can_remove_a_search_from_the_list_of_saved_searches_if_the_uuid_is_not_in_it(self):
        # Setup
        request = RequestFactory().post('/')
        request.user = AnonymousUser()
        SessionMiddleware().process_request(request)
        view = SavedSearchRemoveView.as_view()
        searches = SavedSearchList(request)
        searches.add('foo=bar&xyz=test', 100)
        searches.save()
        # Run
        response = view(request, 'unknown')
        # Check
        assert response.status_code == 200
        searches = SavedSearchList(request)
        assert len(searches) == 1
