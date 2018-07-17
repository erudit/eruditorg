# -*- coding: utf-8 -*-
import pytest

import unittest.mock

from django.core.cache import cache
from django.test import TestCase
from eruditarticle.objects import EruditArticle

from erudit.fedora.modelmixins import FedoraMixin
from erudit.fedora.objects import ArticleDigitalObject


class DummyModel(FedoraMixin):
    localidentifier = 'dummy139'

    def get_fedora_model(self):
        return ArticleDigitalObject

    def get_erudit_class(self):
        return EruditArticle


class TestFedoraMixin:
    def test_can_return_the_pid_of_the_object(self):
        # Setup
        obj = DummyModel()
        # Run & check
        assert obj.get_full_identifier() == 'dummy139'
        assert obj.pid == 'dummy139'

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

    @unittest.mock.patch.object(ArticleDigitalObject, 'erudit_xsd300')
    @unittest.mock.patch.object(ArticleDigitalObject, '_get_datastreams')
    def test_can_return_the_erudit_object(self, mock_ds, mock_xsd300):
        # Setup
        mock_ds.return_value = ['ERUDITXSD300', ]  # noqa
        mock_xsd300.content = unittest.mock.MagicMock()
        mock_xsd300.content.serialize = unittest.mock.MagicMock(return_value='<article></article>')
        obj = DummyModel()
        # Run & check
        assert isinstance(obj.get_erudit_object(), EruditArticle)
        assert isinstance(obj.erudit_object, EruditArticle)

    @unittest.mock.patch('erudit.fedora.modelmixins.cache')
    @unittest.mock.patch.object(ArticleDigitalObject, 'erudit_xsd300')
    @unittest.mock.patch.object(ArticleDigitalObject, '_get_datastreams')
    def test_can_set_the_xml_content_in_the_cache_if_it_is_not_there_already(
            self, mock_ds, mock_xsd300, mock_cache):
        # Setup
        mock_ds.return_value = ['ERUDITXSD300', ]  # noqa
        mock_xsd300.content = unittest.mock.MagicMock()
        mock_xsd300.content.serialize = unittest.mock.MagicMock(return_value='<article></article>')
        mock_cache.get.return_value = None
        obj = DummyModel()
        # Run
        dummy = obj.erudit_object, EruditArticle  # noqa
        # Check
        assert mock_cache.get.call_count == 1
        assert mock_cache.set.call_count == 1

    @unittest.mock.patch('erudit.fedora.modelmixins.cache')
    @unittest.mock.patch.object(ArticleDigitalObject, 'erudit_xsd300')
    @unittest.mock.patch.object(ArticleDigitalObject, '_get_datastreams')
    def test_can_fetch_the_xml_content_from_the_cache_if_applicable(
            self, mock_ds, mock_xsd300, mock_cache):
        # Setup
        mock_ds.return_value = ['ERUDITXSD300', ]  # noqa
        mock_xsd300.content = unittest.mock.MagicMock()
        mock_xsd300.content.serialize = unittest.mock.MagicMock(return_value='<article></article>')
        mock_cache.get.return_value = '<article></article>'
        obj = DummyModel()
        # Run
        dummy = obj.erudit_object, EruditArticle  # noqa
        # Check
        assert mock_cache.get.call_count == 1
        assert mock_cache.set.call_count == 0
