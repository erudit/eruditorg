# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse

from erudit.test.factories import AuthorFactory
from erudit.test.factories import CollectionFactory
from erudit.test.factories import ThesisFactory

from base.test.testcases import EruditClientTestCase


class TestThesisHomeView(EruditClientTestCase):
    def test_inserts_collection_information_into_the_context(self):
        # Setup
        author = AuthorFactory.create()
        collection_1 = CollectionFactory.create()
        collection_2 = CollectionFactory.create()
        thesis_1 = ThesisFactory.create(  # noqa
            localidentifier='thesis-1', collection=collection_1, author=author,
            publication_year=2010)
        thesis_2 = ThesisFactory.create(
            localidentifier='thesis-2', collection=collection_1, author=author,
            publication_year=2012)
        thesis_3 = ThesisFactory.create(
            localidentifier='thesis-3', collection=collection_1, author=author,
            publication_year=2013)
        thesis_4 = ThesisFactory.create(
            localidentifier='thesis-4', collection=collection_1, author=author,
            publication_year=2014)
        thesis_5 = ThesisFactory.create(  # noqa
            localidentifier='thesis-5', collection=collection_2, author=author,
            publication_year=2010)
        thesis_6 = ThesisFactory.create(
            localidentifier='thesis-6', collection=collection_2, author=author,
            publication_year=2012)
        thesis_7 = ThesisFactory.create(
            localidentifier='thesis-7', collection=collection_2, author=author,
            publication_year=2013)
        thesis_8 = ThesisFactory.create(
            localidentifier='thesis-8', collection=collection_2, author=author,
            publication_year=2014)
        url = reverse('public:thesis:home')
        # Run
        response = self.client.get(url)
        # Check
        assert response.status_code == 200
        assert 'collections_dict' in response.context
        assert len(response.context['collections_dict']) == 2
        assert collection_1.id in response.context['collections_dict']
        assert collection_2.id in response.context['collections_dict']
        assert response.context['collections_dict'][collection_1.id]['thesis_count'] == 4
        assert response.context['collections_dict'][collection_2.id]['thesis_count'] == 4
        assert response.context['collections_dict'][collection_1.id]['recent_theses'] == \
            [thesis_4, thesis_3, thesis_2, ]
        assert response.context['collections_dict'][collection_2.id]['recent_theses'] == \
            [thesis_8, thesis_7, thesis_6, ]


class TestThesisCollectionHomeView(EruditClientTestCase):
    def test_inserts_the_recent_theses_into_the_context(self):
        # Setup
        author = AuthorFactory.create()
        collection = CollectionFactory.create()
        thesis_1 = ThesisFactory.create(  # noqa
            localidentifier='thesis-1', collection=collection, author=author,
            publication_year=2010)
        thesis_2 = ThesisFactory.create(
            localidentifier='thesis-2', collection=collection, author=author,
            publication_year=2012)
        thesis_3 = ThesisFactory.create(
            localidentifier='thesis-3', collection=collection, author=author,
            publication_year=2013)
        thesis_4 = ThesisFactory.create(
            localidentifier='thesis-4', collection=collection, author=author,
            publication_year=2014)
        url = reverse('public:thesis:collection_home', args=(collection.id, ))
        # Run
        response = self.client.get(url)
        # Check
        assert response.status_code == 200
        assert response.context['recent_theses'] == [thesis_4, thesis_3, thesis_2, ]

    def test_inserts_the_thesis_count_into_the_context(self):
        # Setup
        author = AuthorFactory.create()
        collection = CollectionFactory.create()
        thesis_1 = ThesisFactory.create(  # noqa
            localidentifier='thesis-1', collection=collection, author=author,
            publication_year=2010)
        thesis_2 = ThesisFactory.create(  # noqa
            localidentifier='thesis-2', collection=collection, author=author,
            publication_year=2012)
        thesis_3 = ThesisFactory.create(  # noqa
            localidentifier='thesis-3', collection=collection, author=author,
            publication_year=2013)
        thesis_4 = ThesisFactory.create(  # noqa
            localidentifier='thesis-4', collection=collection, author=author,
            publication_year=2014)
        url = reverse('public:thesis:collection_home', args=(collection.id, ))
        # Run
        response = self.client.get(url)
        # Check
        assert response.status_code == 200
        assert response.context['thesis_count'] == 4

    def test_inserts_the_thesis_counts_grouped_by_publication_years(self):
        # Setup
        author = AuthorFactory.create()
        collection = CollectionFactory.create()
        thesis_1 = ThesisFactory.create(  # noqa
            localidentifier='thesis-1', collection=collection, author=author,
            publication_year=2010)
        thesis_2 = ThesisFactory.create(  # noqa
            localidentifier='thesis-2', collection=collection, author=author,
            publication_year=2012)
        thesis_3 = ThesisFactory.create(  # noqa
            localidentifier='thesis-3', collection=collection, author=author,
            publication_year=2013)
        thesis_4 = ThesisFactory.create(  # noqa
            localidentifier='thesis-4', collection=collection, author=author,
            publication_year=2014)
        thesis_5 = ThesisFactory.create(  # noqa
            localidentifier='thesis-5', collection=collection, author=author,
            publication_year=2012)
        thesis_6 = ThesisFactory.create(  # noqa
            localidentifier='thesis-6', collection=collection, author=author,
            publication_year=2012)
        thesis_7 = ThesisFactory.create(  # noqa
            localidentifier='thesis-7', collection=collection, author=author,
            publication_year=2014)
        url = reverse('public:thesis:collection_home', args=(collection.id, ))
        # Run
        response = self.client.get(url)
        # Check
        assert response.status_code == 200
        assert response.context['thesis_groups']['by_publication_year'][0] == \
            {'publication_year': 2014, 'total': 2}
        assert response.context['thesis_groups']['by_publication_year'][1] == \
            {'publication_year': 2013, 'total': 1}
        assert response.context['thesis_groups']['by_publication_year'][2] == \
            {'publication_year': 2012, 'total': 3}
        assert response.context['thesis_groups']['by_publication_year'][3] == \
            {'publication_year': 2010, 'total': 1}

    def test_inserts_the_thesis_counts_grouped_by_author_name(self):
        # Setup
        author_1 = AuthorFactory.create(lastname='Aname')
        author_2 = AuthorFactory.create(lastname='Bname')
        author_3 = AuthorFactory.create(lastname='Cname')
        author_4 = AuthorFactory.create(lastname='Dname')
        collection = CollectionFactory.create()
        thesis_1 = ThesisFactory.create(  # noqa
            localidentifier='thesis-1', collection=collection, author=author_1,
            publication_year=2010)
        thesis_2 = ThesisFactory.create(  # noqa
            localidentifier='thesis-2', collection=collection, author=author_2,
            publication_year=2012)
        thesis_3 = ThesisFactory.create(  # noqa
            localidentifier='thesis-3', collection=collection, author=author_3,
            publication_year=2013)
        thesis_4 = ThesisFactory.create(  # noqa
            localidentifier='thesis-4', collection=collection, author=author_4,
            publication_year=2014)
        thesis_5 = ThesisFactory.create(  # noqa
            localidentifier='thesis-5', collection=collection, author=author_2,
            publication_year=2012)
        thesis_6 = ThesisFactory.create(  # noqa
            localidentifier='thesis-6', collection=collection, author=author_2,
            publication_year=2012)
        thesis_7 = ThesisFactory.create(  # noqa
            localidentifier='thesis-7', collection=collection, author=author_4,
            publication_year=2014)
        url = reverse('public:thesis:collection_home', args=(collection.id, ))
        # Run
        response = self.client.get(url)
        # Check
        assert response.status_code == 200
        assert response.context['thesis_groups']['by_author_name'][0] == \
            {'author_firstletter': 'A', 'total': 1}
        assert response.context['thesis_groups']['by_author_name'][1] == \
            {'author_firstletter': 'B', 'total': 3}
        assert response.context['thesis_groups']['by_author_name'][2] == \
            {'author_firstletter': 'C', 'total': 1}
        assert response.context['thesis_groups']['by_author_name'][3] == \
            {'author_firstletter': 'D', 'total': 2}
