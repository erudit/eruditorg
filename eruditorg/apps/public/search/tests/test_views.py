# -*- coding: utf-8 -*-

import json
import unittest.mock

from django.core.urlresolvers import reverse
from django.test import RequestFactory
from django.utils.encoding import smart_text
from django.utils.timezone import now

from core.solrq.query import Query
from erudit.factories import ArticleFactory
from erudit.factories import IssueFactory
from erudit.fedora.modelmixins import FedoraMixin
from erudit.models import Article
from erudit.tests.base import BaseEruditTestCase

from ..views import EruditDocumentListAPIView


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
    m.authors = [{'firstname': 'Test', 'lastname': 'Foobar'}]
    return m


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
