# -*- coding: utf-8 -*-

from django.test import TestCase
from eruditarticle.objects import EruditJournal

from erudit.fedora.modelmixins import FedoraMixin
from erudit.fedora.objects import JournalDigitalObject


class DummyModel(FedoraMixin):
    localidentifier = 'dummy139'

    def get_fedora_model(self):
        return JournalDigitalObject

    def get_erudit_class(self):
        return EruditJournal


class TestFedoraMixin(TestCase):
    def test_can_return_the_pid_of_the_object(self):
        # Setup
        obj = DummyModel()
        # Run & check
        self.assertEqual(obj.get_pid(), 'erudit:erudit.dummy139')
        self.assertEqual(obj.pid, 'erudit:erudit.dummy139')

    def test_can_return_the_eulfedora_model(self):
        # Setup
        obj = DummyModel()
        # Run & check
        self.assertEqual(obj.get_fedora_model(), JournalDigitalObject)
        self.assertEqual(obj.fedora_model, JournalDigitalObject)

    def test_can_return_the_eulfedora_object(self):
        # Setup
        obj = DummyModel()
        # Run & check
        self.assertTrue(isinstance(obj.get_fedora_object(), JournalDigitalObject))
        self.assertTrue(isinstance(obj.fedora_object, JournalDigitalObject))

    def test_can_return_the_erudit_class(self):
        # Setup
        obj = DummyModel()
        # Run & check
        self.assertEqual(obj.get_erudit_class(), EruditJournal)
        self.assertEqual(obj.erudit_class, EruditJournal)

    def test_can_return_the_erudit_object(self):
        # Setup
        obj = DummyModel()
        # Run & check
        self.assertTrue(isinstance(obj.get_erudit_object(), EruditJournal))
        self.assertTrue(isinstance(obj.erudit_object, EruditJournal))
