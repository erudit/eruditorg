# -*- coding: utf-8 -*-

import pytest

from erudit.test.factories import AuthorFactory
from erudit.test.factories import CollectionFactory
from erudit.test.factories import ThesisFactory

from core.thesis.shortcuts import get_thesis_collections


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
