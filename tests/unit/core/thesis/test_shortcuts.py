# -*- coding: utf-8 -*-

import pytest

from erudit.models import Thesis
from erudit.test.factories import AuthorFactory
from erudit.test.factories import CollectionFactory
from erudit.test.factories import ThesisFactory

from core.thesis.shortcuts import get_thesis_collections
from core.thesis.shortcuts import get_thesis_counts_per_author_first_letter
from core.thesis.shortcuts import get_thesis_counts_per_publication_year


@pytest.mark.django_db
class TestGetThesisCollectionsShortcut(object):
    def test_returns_only_collections_associated_with_theses(self):
        # Setup
        author = AuthorFactory.create()
        collection_1 = CollectionFactory.create(localidentifier='col1')
        collection_2 = CollectionFactory.create(localidentifier='col2')
        CollectionFactory.create(localidentifier='col3')
        ThesisFactory.create(localidentifier='thesis1', collection=collection_1, author=author)
        ThesisFactory.create(localidentifier='thesis2', collection=collection_2, author=author)
        # Run & check
        assert list(get_thesis_collections()) == [collection_1, collection_2, ]


@pytest.mark.django_db
class TestGetThesisCountsPerPublicationYearShortcut(object):
    def test_can_determine_the_thesis_counts_per_publication_year(self):
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
        # Run
        aggs = get_thesis_counts_per_publication_year(Thesis.objects.all())
        # Check
        assert aggs[0] == {'publication_year': 2014, 'total': 2}
        assert aggs[1] == {'publication_year': 2013, 'total': 1}
        assert aggs[2] == {'publication_year': 2012, 'total': 3}
        assert aggs[3] == {'publication_year': 2010, 'total': 1}


@pytest.mark.django_db
class TestGetThesisCountsPerAuthorFirstLetterShortcut(object):
    def test_can_determine_the_thesis_counts_per_author_firstletter(self):
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
        # Run
        aggs = get_thesis_counts_per_author_first_letter(Thesis.objects.all())
        # Check
        assert aggs[0] == {'author_firstletter': 'A', 'total': 1}
        assert aggs[1] == {'author_firstletter': 'B', 'total': 3}
        assert aggs[2] == {'author_firstletter': 'C', 'total': 1}
        assert aggs[3] == {'author_firstletter': 'D', 'total': 2}
