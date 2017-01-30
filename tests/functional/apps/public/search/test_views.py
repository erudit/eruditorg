# -*- coding: utf-8 -*-

import json
import unittest.mock

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
from erudit.fedora.modelmixins import FedoraMixin
from erudit.models import Article

from apps.public.search.saved_searches import SavedSearchList
from apps.public.search.views import AdvancedSearchView
from apps.public.search.views import EruditDocumentListAPIView
from apps.public.search.views import SavedSearchAddView
from apps.public.search.views import SavedSearchRemoveView


def fake_get_results(**kwargs):
    results = unittest.mock.Mock()
    results.docs = [{'ID': a.localidentifier} for a in Article.objects.all()]
    results.facets = {'facet_fields': {'Corpus_fac': ['val1', 12, 'val2', 14, ], }}
    results.hits = 50
    return results


def get_mocked_erudit_object():
    m = unittest.mock.MagicMock()
    m.number = 2
    m.subtitle = 'Foo bar'
    m.first_page = 10
    m.last_page = 12
    m.abstracts = [{'lang': 'fr', 'content': 'This is a test'}]
    m.get_authors = lambda: [{'firstname': 'Test', 'lastname': 'Foobar'}]
    m.get_reviewed_works = lambda: []
    return m


@override_settings(DEBUG=True)
class TestEruditDocumentListAPIView(BaseEruditTestCase):
    def setUp(self):
        super(TestEruditDocumentListAPIView, self).setUp()
        self.factory = RequestFactory()

    @unittest.mock.patch.object(FedoraMixin, 'get_erudit_object')
    @unittest.mock.patch.object(Query, 'get_results')
    def test_can_return_erudit_documents(self, mock_get_results, mock_erudit_object):
        # Setup
        mock_get_results.side_effect = fake_get_results
        mock_erudit_object.return_value = get_mocked_erudit_object()
        issue = IssueFactory.create(journal=self.journal, date_published=now())
        localidentifiers = []
        for i in range(0, 50):
            lid = 'lid-{0}'.format(i)
            localidentifiers.append(lid)
            ArticleFactory.create(issue=issue, localidentifier=lid)

        request = self.factory.get('/', data={'format': 'json'})
        list_view = EruditDocumentListAPIView.as_view()

        # Run
        results_data = list_view(request).render().content
        # Check
        results = json.loads(smart_text(results_data))
        self.assertEqual(results['pagination']['count'], 50)

    @unittest.mock.patch.object(FedoraMixin, 'get_fedora_object')
    @unittest.mock.patch.object(Query, 'get_results')
    def test_can_return_erudit_documents_not_in_fedora(self, mock_get_results, mock_fedora_object):
        # Setup
        mock_get_results.side_effect = fake_get_results
        mock_fedora_object.return_value = None
        issue = IssueFactory.create(journal=self.journal, date_published=now())
        localidentifiers = []
        for i in range(0, 1):
            lid = 'lid-{0}'.format(i)
            localidentifiers.append(lid)
            ArticleFactory.create(issue=issue, localidentifier=lid)

        request = self.factory.get('/', data={'format': 'json'})
        list_view = EruditDocumentListAPIView.as_view()

        # Run
        results_data = list_view(request).render().content
        # Check
        results = json.loads(smart_text(results_data))
        self.assertEqual(results['pagination']['count'], 50)


@pytest.mark.django_db
class TestAdvancedSearchView(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        self.factory = RequestFactory()

    def test_can_insert_the_saved_searches_into_the_context(self):
        # Setup
        url = reverse('public:search:advanced_search')
        request = self.factory.get(url)
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


@pytest.mark.django_db
class TestSavedSearchAddView(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        self.factory = RequestFactory()

    def test_can_add_a_search_to_the_list_of_saved_searches(self):
        # Setup
        request = self.factory.post('/', {'querystring': 'foo=bar&xyz=test', 'results_count': 100})
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
        request = self.factory.post('/', {'results_count': 100})
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
        request = self.factory.post('/', {'querystring': 'foo=bar&xyz=test'})
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
        request = self.factory.post('/', {'querystring': 'bad', 'results_count': 100})
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
        request = self.factory.post(
            '/', {'querystring': 'foo=bar&xyz=test', 'results_count': 'bad'})
        request.user = AnonymousUser()
        SessionMiddleware().process_request(request)
        view = SavedSearchAddView.as_view()
        # Run
        view(request)
        # Check
        searches = SavedSearchList(request)
        assert not len(searches)


@pytest.mark.django_db
class TestSavedSearchRemoveView(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        self.factory = RequestFactory()

    def test_can_remove_a_search_from_the_list_of_saved_searches(self):
        # Setup
        request = self.factory.post('/')
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
        request = self.factory.post('/')
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
