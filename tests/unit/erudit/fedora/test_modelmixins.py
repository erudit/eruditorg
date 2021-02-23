# -*- coding: utf-8 -*-
import pytest

import unittest.mock

from django.core.cache import cache
from django.test import TestCase
from eruditarticle.objects import EruditArticle

from erudit.fedora import repository
from erudit.fedora.modelmixins import FedoraMixin
from erudit.fedora.objects import ArticleDigitalObject
from erudit.test.factories import ArticleFactory, IssueFactory, JournalFactory


class DummyModel(FedoraMixin):
    localidentifier = "erudit:erudit.ae49.ae3958.045074ar"

    def __init__(self):
        repository.api.register_pid(self.localidentifier)

    def get_erudit_content_url(self):
        return f"objects/{self.pid}/datastreams/ERUDITXSD300/content"

    def get_fedora_model(self):
        return ArticleDigitalObject

    def get_erudit_class(self):
        return EruditArticle


class TestFedoraMixin:
    def test_is_in_fedora(self):
        obj = DummyModel()
        obj.get_erudit_content_url = (
            lambda: "objects/erudit:erudit.journal.issue.article/datastreams/ERUDITXSD300/content"
        )
        assert obj.is_in_fedora == False

    def test_can_return_the_pid_of_the_object(self):
        # Setup
        obj = DummyModel()
        # Run & check
        assert obj.get_full_identifier() == "erudit:erudit.ae49.ae3958.045074ar"
        assert obj.pid == "erudit:erudit.ae49.ae3958.045074ar"

    def test_can_return_the_eulfedora_model(self):
        # Setup
        obj = DummyModel()
        # Run & check
        assert obj.get_fedora_model() == ArticleDigitalObject
        assert obj.fedora_model == ArticleDigitalObject

    def test_can_return_the_eulfedora_object(self):
        # Setup
        obj = DummyModel()
        # Run & check
        assert isinstance(obj.get_fedora_object(), ArticleDigitalObject)
        assert isinstance(obj.fedora_object, ArticleDigitalObject)

    def test_can_return_the_erudit_class(self):
        # Setup
        obj = DummyModel()
        # Run & check
        assert obj.get_erudit_class() == EruditArticle
        assert obj.erudit_class == EruditArticle

    @unittest.mock.patch.object(ArticleDigitalObject, "erudit_xsd300")
    @unittest.mock.patch.object(ArticleDigitalObject, "_get_datastreams")
    def test_can_return_the_erudit_object(self, mock_ds, mock_xsd300):
        # Setup
        mock_ds.return_value = [
            "ERUDITXSD300",
        ]  # noqa
        mock_xsd300.content = unittest.mock.MagicMock()
        mock_xsd300.content.serialize = unittest.mock.MagicMock(return_value="<article></article>")
        obj = DummyModel()
        # Run & check
        assert isinstance(obj.get_erudit_object(), EruditArticle)
        assert isinstance(obj.erudit_object, EruditArticle)

    @unittest.mock.patch("erudit.fedora.modelmixins.cache")
    @unittest.mock.patch.object(ArticleDigitalObject, "erudit_xsd300")
    @unittest.mock.patch.object(ArticleDigitalObject, "_get_datastreams")
    def test_can_set_the_xml_content_in_the_cache_if_it_is_not_there_already(
        self, mock_ds, mock_xsd300, mock_cache
    ):
        # Setup
        mock_ds.return_value = [
            "ERUDITXSD300",
        ]  # noqa
        mock_xsd300.content = unittest.mock.MagicMock()
        mock_xsd300.content.serialize = unittest.mock.MagicMock(return_value="<article></article>")
        mock_cache.get.return_value = None
        obj = DummyModel()
        # Run
        dummy = obj.erudit_object, EruditArticle  # noqa
        # Check
        assert mock_cache.get.call_count == 1
        assert mock_cache.set.call_count == 1

    @unittest.mock.patch("erudit.fedora.modelmixins.cache")
    @unittest.mock.patch.object(ArticleDigitalObject, "erudit_xsd300")
    @unittest.mock.patch.object(ArticleDigitalObject, "_get_datastreams")
    def test_can_fetch_the_xml_content_from_the_cache_if_applicable(
        self, mock_ds, mock_xsd300, mock_cache
    ):
        # Setup
        mock_ds.return_value = [
            "ERUDITXSD300",
        ]  # noqa
        mock_xsd300.content = unittest.mock.MagicMock()
        mock_xsd300.content.serialize = unittest.mock.MagicMock(return_value="<article></article>")
        mock_cache.get.return_value = "<article></article>"
        obj = DummyModel()
        # Run
        dummy = obj.erudit_object, EruditArticle  # noqa
        # Check
        assert mock_cache.get.call_count == 1
        assert mock_cache.set.call_count == 0

    @pytest.mark.django_db
    @pytest.mark.parametrize("ModelFactory", (ArticleFactory, IssueFactory, JournalFactory))
    @unittest.mock.patch("erudit.fedora.modelmixins.cache")
    def test_uses_localidentifier_of_the_model_as_the_cache_key(self, mock_cache, ModelFactory):
        mock_cache.get.return_value = None
        model = ModelFactory(localidentifier="test")
        # Fetch the erudit_object to make a call to Fedora
        _ = model.erudit_object
        # The mock_calls list contains a list of call tuples
        mock_name, call_args, call_kwargs = mock_cache.set.mock_calls[0]
        key, content, duration = call_args
        assert key == model.localidentifier
