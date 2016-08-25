# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse

from erudit.test.factories import AuthorFactory
from erudit.test.factories import SearchUnitCollectionFactory
from erudit.test.factories import SearchUnitDocumentFactory
from erudit.test.factories import SearchUnitFactory

from base.test.testcases import EruditClientTestCase


class TestSearchUnitListView(EruditClientTestCase):
    def test_embeds_the_total_count_of_search_units_into_the_context(self):
        # Setup
        search_unit_1 = SearchUnitFactory.create(collection=self.collection)
        search_unit_2 = SearchUnitFactory.create(collection=self.collection)
        search_unit_collection_1 = SearchUnitCollectionFactory.create(search_unit=search_unit_1)
        search_unit_collection_2 = SearchUnitCollectionFactory.create(search_unit=search_unit_2)
        SearchUnitDocumentFactory(collection=search_unit_collection_1)
        SearchUnitDocumentFactory(collection=search_unit_collection_1)
        SearchUnitDocumentFactory(collection=search_unit_collection_2)
        url = reverse('public:grey_literature:search_unit_list')
        # Run
        response = self.client.get(url)
        # Check
        assert response.status_code == 200
        assert response.context['global_search_units_count'] == 2

    def test_embeds_the_total_count_of_search_unit_documents_into_the_context(self):
        # Setup
        search_unit_1 = SearchUnitFactory.create(collection=self.collection)
        search_unit_2 = SearchUnitFactory.create(collection=self.collection)
        search_unit_collection_1 = SearchUnitCollectionFactory.create(search_unit=search_unit_1)
        search_unit_collection_2 = SearchUnitCollectionFactory.create(search_unit=search_unit_2)
        SearchUnitDocumentFactory(collection=search_unit_collection_1)
        SearchUnitDocumentFactory(collection=search_unit_collection_1)
        SearchUnitDocumentFactory(collection=search_unit_collection_2)
        url = reverse('public:grey_literature:search_unit_list')
        # Run
        response = self.client.get(url)
        # Check
        assert response.status_code == 200
        assert response.context['global_documents_count'] == 3

    def test_embeds_the_total_count_of_search_unit_document_authors_into_the_context(self):
        # Setup
        search_unit_1 = SearchUnitFactory.create(collection=self.collection)
        search_unit_2 = SearchUnitFactory.create(collection=self.collection)
        search_unit_collection_1 = SearchUnitCollectionFactory.create(search_unit=search_unit_1)
        search_unit_collection_2 = SearchUnitCollectionFactory.create(search_unit=search_unit_2)
        document_1 = SearchUnitDocumentFactory(collection=search_unit_collection_1)
        document_2 = SearchUnitDocumentFactory(collection=search_unit_collection_1)
        document_3 = SearchUnitDocumentFactory(collection=search_unit_collection_2)
        author_1 = AuthorFactory.create()
        author_2 = AuthorFactory.create()
        author_3 = AuthorFactory.create()
        author_4 = AuthorFactory.create()
        author_5 = AuthorFactory.create()
        document_1.authors.add(author_1, author_2)
        document_2.authors.add(author_2, author_3)
        document_3.authors.add(author_1, author_4, author_5)
        url = reverse('public:grey_literature:search_unit_list')
        # Run
        response = self.client.get(url)
        # Check
        assert response.status_code == 200
        assert response.context['global_authors_count'] == 5


class TestSearchUnitDetailView(EruditClientTestCase):
    def test_embeds_the_new_documents_into_the_context(self):
        # Setup
        search_unit = SearchUnitFactory.create(collection=self.collection)
        search_unit_collection_1 = SearchUnitCollectionFactory.create(search_unit=search_unit)
        search_unit_collection_2 = SearchUnitCollectionFactory.create(search_unit=search_unit)
        SearchUnitDocumentFactory(collection=search_unit_collection_1, publication_year=2011)
        SearchUnitDocumentFactory(collection=search_unit_collection_1, publication_year=2012)
        document_3 = SearchUnitDocumentFactory(collection=search_unit_collection_1, publication_year=2013)  # noqa
        document_4 = SearchUnitDocumentFactory(collection=search_unit_collection_2, publication_year=2014)  # noqa
        document_5 = SearchUnitDocumentFactory(collection=search_unit_collection_2, publication_year=2015)  # noqa
        url = reverse('public:grey_literature:search_unit_detail', args=(search_unit.code, ))
        # Run
        response = self.client.get(url)
        # Check
        assert response.status_code == 200
        assert list(response.context['new_documents']) == [document_5, document_4, document_3, ]

    def test_embeds_the_collections_into_the_context(self):
        # Setup
        search_unit_1 = SearchUnitFactory.create(collection=self.collection)
        search_unit_2 = SearchUnitFactory.create(collection=self.collection)
        search_unit_collection_1 = SearchUnitCollectionFactory.create(search_unit=search_unit_1)
        search_unit_collection_2 = SearchUnitCollectionFactory.create(search_unit=search_unit_2)
        search_unit_collection_3 = SearchUnitCollectionFactory.create(search_unit=search_unit_2)
        SearchUnitDocumentFactory(collection=search_unit_collection_1)
        SearchUnitDocumentFactory(collection=search_unit_collection_2)
        SearchUnitDocumentFactory(collection=search_unit_collection_3)
        url = reverse('public:grey_literature:search_unit_detail', args=(search_unit_2.code, ))
        # Run
        response = self.client.get(url)
        # Check
        assert response.status_code == 200
        assert set(response.context['collections']) == \
            set([search_unit_collection_2, search_unit_collection_3, ])


class TestSearchUnitCollectionDetailView(EruditClientTestCase):
    def test_browsing_works(self):
        # Setup
        search_unit_1 = SearchUnitFactory.create(collection=self.collection)
        search_unit_2 = SearchUnitFactory.create(collection=self.collection)
        search_unit_collection_1 = SearchUnitCollectionFactory.create(search_unit=search_unit_1)
        search_unit_collection_2 = SearchUnitCollectionFactory.create(search_unit=search_unit_2)
        search_unit_collection_3 = SearchUnitCollectionFactory.create(search_unit=search_unit_2)
        SearchUnitDocumentFactory(collection=search_unit_collection_1)
        SearchUnitDocumentFactory(collection=search_unit_collection_2)
        SearchUnitDocumentFactory(collection=search_unit_collection_3)
        url = reverse(
            'public:grey_literature:collection_detail',
            args=(search_unit_2.code, search_unit_collection_3.localidentifier, ))
        # Run
        response = self.client.get(url)
        # Check
        assert response.status_code == 200


class TestSearchUnitDocumentDetailView(EruditClientTestCase):
    def test_embeds_the_related_articles_into_the_context(self):
        # Setup
        search_unit = SearchUnitFactory.create(collection=self.collection)
        search_unit_collection_1 = SearchUnitCollectionFactory.create(search_unit=search_unit)
        search_unit_collection_2 = SearchUnitCollectionFactory.create(search_unit=search_unit)
        search_unit_collection_3 = SearchUnitCollectionFactory.create(search_unit=search_unit)
        document_1 = SearchUnitDocumentFactory(collection=search_unit_collection_1)
        document_2 = SearchUnitDocumentFactory(collection=search_unit_collection_2)
        document_3 = SearchUnitDocumentFactory(collection=search_unit_collection_3)
        document_4 = SearchUnitDocumentFactory(collection=search_unit_collection_1)
        document_5 = SearchUnitDocumentFactory(collection=search_unit_collection_2)
        url = reverse(
            'public:grey_literature:document_detail', args=(
                search_unit.code, search_unit_collection_1.localidentifier,
                document_1.localidentifier))
        # Run
        response = self.client.get(url)
        # Check
        assert response.status_code == 200
        assert set(response.context['related_documents']) == \
            set([document_2, document_3, document_4, document_5, ])
