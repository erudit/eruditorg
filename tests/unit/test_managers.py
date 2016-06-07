# -*- coding: utf-8 -*-

from erudit.models import Journal
from erudit.test import BaseEruditTestCase
from erudit.test.factories import JournalFactory


class TestJournalUpcomingManager(BaseEruditTestCase):
    def test_returns_only_the_upcoming_journals(self):
        # Setup
        journal_1 = JournalFactory.create(collection=self.collection, upcoming=True)
        JournalFactory.create(collection=self.collection, upcoming=False)
        # Run
        journals = Journal.upcoming_objects.all()
        # Check
        self.assertEqual(list(journals), [journal_1, ])
