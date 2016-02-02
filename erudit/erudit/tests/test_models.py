# -*- coding: utf-8 -*-

from eruditarticle.objects import EruditJournal

from erudit.fedora.objects import JournalDigitalObject

from .base import BaseEruditTestCase


class TestJournal(BaseEruditTestCase):
    def test_can_return_the_associated_eulfedora_model(self):
        # Run & check
        self.assertEqual(self.journal.fedora_model, JournalDigitalObject)

    def test_can_return_the_associated_erudit_class(self):
        # Run & check
        self.assertEqual(self.journal.erudit_class, EruditJournal)
