# -*- coding: utf-8 -*-
import pytest

import unittest.mock

from eruditarticle.objects import EruditArticle

from erudit.fedora import repository
from erudit.fedora.modelmixins import FedoraMixin
from erudit.test.factories import ArticleFactory, IssueFactory, JournalFactory


class DummyModel(FedoraMixin):
    localidentifier = "erudit:erudit.ae49.ae3958.045074ar"

    def __init__(self):
        repository.api.register_pid(self.localidentifier)

    def get_erudit_object_datastream_name(self):
        return "ERUDITXSD300"

    def get_erudit_class(self):
        return EruditArticle


class TestFedoraMixin:
    def test_is_in_fedora(self):
        obj = DummyModel()
        obj.get_erudit_object_datastream_name = lambda: "ERUDITXSD300"
        assert obj.is_in_fedora

    def test_can_return_the_pid_of_the_object(self):
        # Setup
        obj = DummyModel()
        # Run & check
        assert obj.get_full_identifier() == "erudit:erudit.ae49.ae3958.045074ar"
        assert obj.pid == "erudit:erudit.ae49.ae3958.045074ar"

    def test_can_return_the_erudit_class(self):
        # Setup
        obj = DummyModel()
        # Run & check
        assert obj.get_erudit_class() == EruditArticle
        assert obj.erudit_class == EruditArticle

    def test_can_return_the_erudit_object(self):
        # Setup
        obj = DummyModel()
        # Run & check
        assert isinstance(obj.erudit_object, EruditArticle)

    @unittest.mock.patch("erudit.fedora.cache.cache")
    def test_can_set_the_xml_content_in_the_cache_if_it_is_not_there_already(self, mock_cache):
        # Setup
        mock_cache.get.return_value = None
        obj = DummyModel()
        # Run
        obj.erudit_object
        # Check
        assert mock_cache.get.call_count == 1
        assert mock_cache.set.call_count == 1

    @unittest.mock.patch("erudit.fedora.cache.cache")
    def test_can_fetch_the_xml_content_from_the_cache_if_applicable(self, mock_cache):
        # Setup
        mock_cache.get.return_value = "<article></article>"
        obj = DummyModel()
        # Run
        obj.erudit_object
        # Check
        assert mock_cache.get.call_count == 1
        assert mock_cache.set.call_count == 0

    @pytest.mark.django_db
    @pytest.mark.parametrize("ModelFactory", (ArticleFactory, IssueFactory, JournalFactory))
    @unittest.mock.patch("erudit.fedora.cache.cache")
    def test_uses_localidentifier_of_the_model_as_the_cache_key(self, mock_cache, ModelFactory):
        mock_cache.get.return_value = None
        model = ModelFactory(localidentifier="test")
        # Fetch the erudit_object to make a call to Fedora
        _ = model.erudit_object
        # The mock_calls list contains a list of call tuples
        mock_name, call_args, call_kwargs = mock_cache.set.mock_calls[0]
        key, content, duration = call_args
        assert key == model.localidentifier
