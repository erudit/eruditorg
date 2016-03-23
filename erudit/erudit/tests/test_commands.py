# -*- coding: utf-8 -*-

from ..factories import JournalFactory, PublisherFactory
from ..models import Publisher
from ..utils.edinum import create_or_update_journal
from ..utils.edinum import create_or_update_publisher

from .base import BaseEruditTestCase


class TestCommands(BaseEruditTestCase):
    def test_create_or_update_publisher(self):
        publisher = create_or_update_publisher("123456", "dcormier")
        self.assertEquals(publisher.name, "dcormier")
        self.assertEquals(publisher.edinum_id, "123456")

        publisher_2 = create_or_update_publisher("123456", "dcormier2")
        self.assertEquals(publisher_2.pk, publisher.pk)
        self.assertEquals(publisher_2.name, "dcormier2")

        # create another publisher with the same edinum_id
        Publisher.objects.create(name="bob", edinum_id="123456")
        publisher = create_or_update_publisher("123456", "dcormier2")
        self.assertIsNone(publisher)

    def test_can_create_journal_and_publisher(self):
        publisher = create_or_update_publisher("123456", "dcormier")
        journal = create_or_update_journal(
            publisher, "123", "Journal of journals", "joj", "", "", None
        )

        self.assertEquals(
            journal.edinum_id, "123"
        )

    def test_can_update_journal(self):
        publisher = create_or_update_publisher("123456", "dcormier")
        journal = create_or_update_journal(
            publisher, "123", "Journal of journals", "joj", "", "", None
        )

        self.assertEquals(
            journal.edinum_id, "123"
        )

        journal_2 = create_or_update_journal(
            publisher, "123", "Journal", "joj", "", "", None
        )

        self.assertEquals(
            journal.pk,
            journal_2.pk
        )

        self.assertEquals(
            journal_2.name,
            "Journal"
        )

    def test_cannot_create_journal_if_nonedinum_journal_exists(self):
        """ Cannot create a journal if a non edinum journal with the same shortname exists """
        publisher = PublisherFactory.create()

        journal = JournalFactory.create(code='testj', edinum_id="123", publishers=[publisher])

        journal = create_or_update_journal(
            publisher, "123", "test", "testj", "", "", None
        )

        self.assertIsNone(journal)
