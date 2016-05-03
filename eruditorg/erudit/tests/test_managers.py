# -*- coding: utf-8 -*-

from erudit.factories import JournalFactory
from erudit.models import Journal

from .base import BaseEruditTestCase


class TestJournalUpcomingManager(BaseEruditTestCase):
    def test_returns_only_the_upcoming_journals(self):
        # Setup
        journal_1 = JournalFactory.create(upcoming=True)
        JournalFactory.create(upcoming=False)
        # Run
        journals = Journal.upcoming_objects.all()
        # Check
        self.assertEqual(list(journals), [journal_1, ])
