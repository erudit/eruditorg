# -*- coding: utf-8 -*-


from django.core.urlresolvers import reverse

from base.test.testcases import EruditClientTestCase
from erudit.test.factories import JournalFactory
from base.test.factories import UserFactory


class TestJournalRoyaltyListView(EruditClientTestCase):
    def test_cannot_be_accessed_by_non_journal_member(self):
        # Setup
        journal = JournalFactory()
        user = UserFactory()

        self.client.login(username=user.username, password="default")
        url = reverse('userspace:journal:royalty_reports:list', args=(journal.pk, ))
        # Run
        response = self.client.get(url)
        # Check
        assert response.status_code == 403

    def test_can_be_accessed_by_a_user_journal_member(self):
        # Setup
        journal = JournalFactory()
        user = UserFactory()
        journal.members.add(user)
        journal.save()

        self.client.login(username=user.username, password="default")
        url = reverse('userspace:journal:royalty_reports:list', args=(journal.pk,))
        # Run
        response = self.client.get(url)
        # Check
        assert response.status_code == 200
