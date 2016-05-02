# -*- coding: utf-8 -*-

import unittest.mock

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


class TestFedoraMixin(TestCase):
    def test_can_return_the_pid_of_the_object(self):
        # Setup
        obj = DummyModel()
        # Run & check
        self.assertEqual(obj.get_full_identifier(), 'dummy139')
        self.assertEqual(obj.pid, 'dummy139')

    def test_can_return_the_eulfedora_model(self):
        # Setup
        obj = DummyModel()
        # Run & check
        self.assertEqual(obj.get_fedora_model(), ArticleDigitalObject)
        self.assertEqual(obj.fedora_model, ArticleDigitalObject)

    def test_can_return_the_eulfedora_object(self):
        # Setup
        obj = DummyModel()
        # Run & check
        self.assertTrue(isinstance(obj.get_fedora_object(), ArticleDigitalObject))
        self.assertTrue(isinstance(obj.fedora_object, ArticleDigitalObject))

    def test_can_return_the_erudit_class(self):
        # Setup
        obj = DummyModel()
        # Run & check
        self.assertEqual(obj.get_erudit_class(), EruditArticle)
        self.assertEqual(obj.erudit_class, EruditArticle)

    @unittest.mock.patch.object(ArticleDigitalObject, 'erudit_xsd300')
    @unittest.mock.patch.object(ArticleDigitalObject, '_get_datastreams')
    def test_can_return_the_erudit_object(self, mock_ds, mock_xsd300):
        # Setup
        mock_ds.return_value = ['ERUDITXSD300', ]  # noqa
        mock_xsd300.content = unittest.mock.MagicMock()
        mock_xsd300.content.serialize = unittest.mock.MagicMock(return_value='<article></article>')
        obj = DummyModel()
        # Run & check
        self.assertTrue(isinstance(obj.get_erudit_object(), EruditArticle))
        self.assertTrue(isinstance(obj.erudit_object, EruditArticle))
