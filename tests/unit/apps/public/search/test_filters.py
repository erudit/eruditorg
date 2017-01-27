# -*- coding: utf-8 -*-

import unittest.mock

from django.test import RequestFactory
from rest_framework.request import Request

from core.solrq.query import Query
from erudit.models import EruditDocument
from erudit.test import BaseEruditTestCase

from apps.public.search.filters import EruditDocumentSolrFilter as BaseEruditDocumentSolrFilter
from apps.public.search.legacy import add_correspondences_to_search_query


def fake_get_results(**kwargs):
    results = unittest.mock.Mock()
    results.docs = []
    results.facets = {'facet_fields': {'Corpus_fac': ['val1', 12, 'val2', 14, ], }}
    return results


class EruditDocumentSolrFilter(BaseEruditDocumentSolrFilter):
    def apply_solr_filters(self, filters):
        sqs = super(EruditDocumentSolrFilter, self).apply_solr_filters(filters)
        self.sqs = sqs
        return sqs


class TestEruditDocumentSolrFilter(BaseEruditTestCase):
    def setUp(self):
        super(TestEruditDocumentSolrFilter, self).setUp()
        self.factory = RequestFactory()

    @unittest.mock.patch.object(Query, 'get_results')
    def test_can_filter_using_a_single_term(self, mock_get_results):
        # Setup
        mock_get_results.side_effect = fake_get_results
        request = Request(self.factory.get('/', data={
            'basic_search_term': 'test',
        }))
        filt = EruditDocumentSolrFilter()
        # Run & check
        filt.filter(request, EruditDocument.objects.all(), None)
        self.assertEqual(filt.sqs._q, '(*:*) AND (TexteComplet:"test")')

    @unittest.mock.patch.object(Query, 'get_results')
    def test_can_filter_using_a_single_term_on_a_specific_field(self, mock_get_results):
        # Setup
        mock_get_results.side_effect = fake_get_results
        request = Request(self.factory.get('/', data={
            'basic_search_term': 'test',
            'basic_search_field': 'meta',
        }))
        filt = EruditDocumentSolrFilter()
        # Run & check
        filt.filter(request, EruditDocument.objects.all(), None)
        self.assertEqual(filt.sqs._q, '(*:*) AND (Metadonnees:"test")')

    @unittest.mock.patch.object(Query, 'get_results')
    def test_can_properly_handle_advanced_queries_using_the_AND_operator(self, mock_get_results):
        # Setup
        mock_get_results.side_effect = fake_get_results
        request = Request(self.factory.get('/', data={
            'basic_search_term': 'test',
            'basic_search_field': 'meta',
            'advanced_search_term1': 'intro',
            'advanced_search_field1': 'all',
            'advanced_search_operator1': 'AND',
        }))
        filt = EruditDocumentSolrFilter()
        # Run & check
        filt.filter(request, EruditDocument.objects.all(), None)
        self.assertEqual(
            filt.sqs._q, '(*:*) AND ((Metadonnees:"test") AND (TexteComplet:"intro"))')

    @unittest.mock.patch.object(Query, 'get_results')
    def test_can_properly_handle_advanced_queries_using_the_OR_operator(self, mock_get_results):
        # Setup
        mock_get_results.side_effect = fake_get_results
        request = Request(self.factory.get('/', data={
            'basic_search_term': 'test',
            'basic_search_field': 'meta',
            'advanced_search_term1': 'intro',
            'advanced_search_field1': 'all',
            'advanced_search_operator1': 'OR',
        }))
        filt = EruditDocumentSolrFilter()
        # Run & check
        filt.filter(request, EruditDocument.objects.all(), None)
        self.assertEqual(filt.sqs._q, '(*:*) AND ((Metadonnees:"test") OR (TexteComplet:"intro"))')

    @unittest.mock.patch.object(Query, 'get_results')
    def test_can_properly_handle_advanced_queries_using_the_negation_operator(self, mock_get_results):  # noqa
        # Setup
        mock_get_results.side_effect = fake_get_results
        request = Request(self.factory.get('/', data={
            'basic_search_term': 'test',
            'basic_search_field': 'meta',
            'advanced_search_term1': 'intro',
            'advanced_search_field1': 'all',
            'advanced_search_operator1': 'NOT',
        }))
        filt = EruditDocumentSolrFilter()
        # Run & check
        filt.filter(request, EruditDocument.objects.all(), None)
        self.assertEqual(
            filt.sqs._q, '(*:*) AND ((Metadonnees:"test") AND ((*:* -TexteComplet:"intro")))')

    @unittest.mock.patch.object(Query, 'get_results')
    def test_can_filter_on_publication_years(self, mock_get_results):
        # Setup
        mock_get_results.side_effect = fake_get_results
        request = Request(self.factory.get('/', data={
            'basic_search_term': 'test',
            'basic_search_field': 'meta',
            'filter_years': [2015, 2016],
        }))
        filt = EruditDocumentSolrFilter()
        # Run & check
        filt.filter(request, EruditDocument.objects.all(), None)
        self.assertEqual(
            filt.sqs._q,
            '(*:*) AND (Metadonnees:"test")'
        )
        self.assertEqual(
            filt.sqs._fq,
            '(*:*) AND (((Annee:"2015")) OR (Annee:"2016"))'
        )

    @unittest.mock.patch.object(Query, 'get_results')
    def test_can_filter_on_a_publication_year_range(self, mock_get_results):
        # Setup
        mock_get_results.side_effect = fake_get_results
        request = Request(self.factory.get('/', data={
            'basic_search_term': 'test',
            'basic_search_field': 'meta',
            'pub_year_start': 2012,
            'pub_year_end': 2016,
        }))
        filt = EruditDocumentSolrFilter()
        # Run & check
        filt.filter(request, EruditDocument.objects.all(), None)

        self.assertEqual(
            filt.sqs._q, '(*:*) AND (Metadonnees:"test")')

        self.assertEqual(
            filt.sqs._fq, '(*:*) AND (Annee:[2012 TO 2016])'
        )

    @unittest.mock.patch.object(Query, 'get_results')
    def test_can_filter_on_document_types(self, mock_get_results):
        # Setup
        mock_get_results.side_effect = fake_get_results
        request = Request(self.factory.get('/', data={
            'basic_search_term': 'test',
            'basic_search_field': 'meta',
            'filter_article_types': ['Article', ],
        }))
        filt = EruditDocumentSolrFilter()
        # Run & check
        filt.filter(request, EruditDocument.objects.all(), None)
        self.assertEqual(
            filt.sqs._q, '(*:*) AND (Metadonnees:"test")')
        self.assertEqual(
            filt.sqs._fq, '(*:*) AND ((TypeArticle_fac:"Article"))')

    @unittest.mock.patch.object(Query, 'get_results')
    def test_can_filter_on_languages(self, mock_get_results):
        # Setup
        mock_get_results.side_effect = fake_get_results
        request_1 = Request(self.factory.get('/', data={
            'basic_search_term': 'test',
            'basic_search_field': 'meta',
            'languages': ['fr', ],
        }))
        request_2 = Request(self.factory.get('/', data={
            'basic_search_term': 'test',
            'basic_search_field': 'meta',
            'filter_languages': ['fr', ],
        }))
        filt_1 = EruditDocumentSolrFilter()
        filt_2 = EruditDocumentSolrFilter()
        # Run & check
        filt_1.filter(request_1, EruditDocument.objects.all(), None)
        filt_2.filter(request_2, EruditDocument.objects.all(), None)
        self.assertEqual(filt_1.sqs._q, '(*:*) AND (Metadonnees:"test")')
        self.assertEqual(filt_1.sqs._fq, '(*:*) AND ((Langue:"fr"))')
        self.assertEqual(filt_2.sqs._q, '(*:*) AND (Metadonnees:"test")')
        self.assertEqual(filt_2.sqs._fq, '(*:*) AND ((Langue:"fr"))')

    @unittest.mock.patch.object(Query, 'get_results')
    def test_can_filter_on_collections(self, mock_get_results):
        # Setup
        mock_get_results.side_effect = fake_get_results
        request_1 = Request(self.factory.get('/', data={
            'basic_search_term': 'test',
            'basic_search_field': 'meta',
            'journals': ['Arborescences', ],
        }))
        request_2 = Request(self.factory.get('/', data={
            'basic_search_term': 'test',
            'basic_search_field': 'meta',
            'filter_collections': ['Arborescences', ],
        }))
        filt_1 = EruditDocumentSolrFilter()
        filt_2 = EruditDocumentSolrFilter()
        # Run & check
        filt_1.filter(request_1, EruditDocument.objects.all(), None)
        filt_2.filter(request_2, EruditDocument.objects.all(), None)
        self.assertEqual(
            filt_1.sqs._q,
            '(*:*) AND (Metadonnees:"test")')

        self.assertEqual(
            filt_1.sqs._fq,
            '(*:*) AND ((TitreCollection_fac:"Arborescences"))')

        self.assertEqual(
            filt_2.sqs._q,
            '(*:*) AND (Metadonnees:"test")')

        self.assertEqual(
            filt_2.sqs._fq,
            '(*:*) AND ((TitreCollection_fac:"Arborescences"))')
    @unittest.mock.patch.object(Query, 'get_results')
    def test_can_filter_on_authors(self, mock_get_results):
        # Setup
        mock_get_results.side_effect = fake_get_results
        request = Request(self.factory.get('/', data={
            'basic_search_term': 'test',
            'basic_search_field': 'meta',
            'filter_authors': ['firstname, lastname', ],
        }))
        filt = EruditDocumentSolrFilter()
        # Run & check
        filt.filter(request, EruditDocument.objects.all(), None)
        self.assertEqual(
            filt.sqs._q,
            '(*:*) AND (Metadonnees:"test")'
        )

        self.assertEqual(
            filt.sqs._fq,
            '(*:*) AND ((Auteur_tri:"firstname, lastname"))'
        )

    @unittest.mock.patch.object(Query, 'get_results')
    def test_can_filter_on_funds(self, mock_get_results):
        # Setup
        mock_get_results.side_effect = fake_get_results
        request_1 = Request(self.factory.get('/', data={
            'basic_search_term': 'test',
            'basic_search_field': 'meta',
            'funds': ['Érudit', ],
        }))
        request_2 = Request(self.factory.get('/', data={
            'basic_search_term': 'test',
            'basic_search_field': 'meta',
            'filter_funds': ['Érudit', ],
        }))
        filt_1 = EruditDocumentSolrFilter()
        filt_2 = EruditDocumentSolrFilter()
        # Run & check
        filt_1.filter(request_1, EruditDocument.objects.all(), None)
        filt_2.filter(request_2, EruditDocument.objects.all(), None)
        self.assertEqual(
            filt_1.sqs._q, '(*:*) AND (Metadonnees:"test")')
        self.assertEqual(
            filt_2.sqs._q, '(*:*) AND (Metadonnees:"test")')

        self.assertEqual(
            filt_1.sqs._fq, '(*:*) AND ((Fonds_fac:"Érudit"))')
        self.assertEqual(
            filt_2.sqs._fq, '(*:*) AND ((Fonds_fac:"Érudit"))')
    @unittest.mock.patch.object(Query, 'get_results')
    def test_can_filter_on_publication_types(self, mock_get_results):
        # Setup
        mock_get_results.side_effect = fake_get_results
        request_1 = Request(self.factory.get('/', data={
            'basic_search_term': 'test',
            'basic_search_field': 'meta',
            'publication_types': ['Culturel', ],
        }))
        request_2 = Request(self.factory.get('/', data={
            'basic_search_term': 'test',
            'basic_search_field': 'meta',
            'filter_publication_types': ['Culturel', ],
        }))
        filt_1 = EruditDocumentSolrFilter()
        filt_2 = EruditDocumentSolrFilter()
        # Run & check
        filt_1.filter(request_1, EruditDocument.objects.all(), None)
        filt_2.filter(request_2, EruditDocument.objects.all(), None)
        self.assertEqual(
            filt_1.sqs._q, '(*:*) AND (Metadonnees:"test")')
        self.assertEqual(
            filt_2.sqs._q, '(*:*) AND (Metadonnees:"test")')
        self.assertEqual(
            filt_1.sqs._fq, '(*:*) AND ((Corpus_fac:"Culturel"))')
        self.assertEqual(
            filt_2.sqs._fq, '(*:*) AND ((Corpus_fac:"Culturel"))')

    @unittest.mock.patch.object(Query, 'get_results')
    def test_can_filter_on_extra_terms(self, mock_get_results):
        # Setup
        mock_get_results.side_effect = fake_get_results
        request = Request(self.factory.get('/', data={
            'basic_search_term': 'test',
            'basic_search_field': 'meta',
            'filter_extra_q': 'foobar',
        }))
        filt = EruditDocumentSolrFilter()
        # Run & check
        filt.filter(request, EruditDocument.objects.all(), None)
        self.assertEqual(
            filt.sqs._q, '(*:*) AND (Metadonnees:"test")')
        self.assertEqual(
            filt.sqs._fq, '(*:*) AND (TexteComplet:"foobar")')

    @unittest.mock.patch.object(Query, 'get_results')
    def test_can_filter_on_disciplines(self, mock_get_results):
        # Setup
        mock_get_results.side_effect = fake_get_results
        request = Request(self.factory.get('/', data={
            'basic_search_term': 'test',
            'basic_search_field': 'meta',
            'disciplines': ['Littérature', ],
        }))
        filt = EruditDocumentSolrFilter()
        # Run & check
        filt.filter(request, EruditDocument.objects.all(), None)
        self.assertEqual(
            filt.sqs._q, '(*:*) AND (Metadonnees:"test")')
        self.assertEqual(
            filt.sqs._fq, '(*:*) AND ((Discipline_fac:"Littérature"))')

    def test_can_properly_determine_the_order_of_the_results(self):
        # Run & check
        request = Request(self.factory.get('/', data={'sort_by': 'relevance'}))
        self.assertEqual(EruditDocumentSolrFilter().get_solr_sorting(request), 'score desc')

        request = Request(self.factory.get('/', data={'sort_by': 'title_asc'}))
        self.assertEqual(EruditDocumentSolrFilter().get_solr_sorting(request), 'Titre_tri asc')

        request = Request(self.factory.get('/', data={'sort_by': 'title_desc'}))
        self.assertEqual(EruditDocumentSolrFilter().get_solr_sorting(request), 'Titre_tri desc')

        request = Request(self.factory.get('/', data={'sort_by': 'author_asc'}))
        self.assertEqual(EruditDocumentSolrFilter().get_solr_sorting(request), 'Auteur_tri asc')

        request = Request(self.factory.get('/', data={'sort_by': 'author_desc'}))
        self.assertEqual(EruditDocumentSolrFilter().get_solr_sorting(request), 'Auteur_tri desc')

        request = Request(self.factory.get('/', data={'sort_by': 'pubdate_asc'}))
        self.assertEqual(
            EruditDocumentSolrFilter().get_solr_sorting(request), 'DateAjoutErudit asc')

        request = Request(self.factory.get('/', data={'sort_by': 'pubdate_desc'}))
        self.assertEqual(
            EruditDocumentSolrFilter().get_solr_sorting(request), 'DateAjoutErudit desc')

    @unittest.mock.patch.object(Query, 'get_results')
    def test_can_properly_return_aggregation_results(self, mock_get_results):
        # Setup
        mock_get_results.side_effect = fake_get_results
        request = Request(self.factory.get('/', data={
            'basic_search_term': 'test',
        }))
        filt = EruditDocumentSolrFilter()
        # Run & check
        _, _, agg = filt.filter(request, EruditDocument.objects.all(), None)
        self.assertEqual(agg, {'publication_type': {'val2': 14, 'val1': 12}})

    def test_can_add_correspondences_to_aggregations(self):
        # Setup
        request = Request(self.factory.get('/', data={
            'basic_search_term': '*',
            'filter_article_type': ['Compte rendu'],
        }))

        correspondences = {
            'Compte rendu': ['Compterendu']
        }

        request_get = add_correspondences_to_search_query(
            request,
            'filter_article_type',
            correspondences
        )

        assert 'Compterendu' in request_get.get('filter_article_type')
