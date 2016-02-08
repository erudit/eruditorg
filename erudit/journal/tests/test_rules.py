# -*- coding: utf-8 -*-

from django.contrib.auth.models import User

from erudit.tests import BaseEruditTestCase


class TestEditJournalRule(BaseEruditTestCase):
    def test_knows_that_a_superuser_can_edit_a_journal(self):
        # Setup
        user = User.objects.create_superuser(
            username='admin', email='admin@xyz.com', password='top_secret')
        # Run & check
        self.assertTrue(user.has_perm('journal.edit_journal'))
        self.assertTrue(user.has_perm('journal.edit_journal', self.journal))

    def test_knows_that_a_staff_member_can_edit_a_journal(self):
        # Setup
        user = User.objects.create_user(
            username='staff', email='admin@xyz.com', password='top_secret')
        user.is_staff = True
        user.save()
        # Run & check
        self.assertTrue(user.has_perm('journal.edit_journal'))
        self.assertTrue(user.has_perm('journal.edit_journal', self.journal))

    def test_knows_if_a_simple_user_can_edit_a_journal(self):
        # Run & check
        self.assertTrue(self.user.has_perm('journal.edit_journal'))
        self.assertTrue(self.user.has_perm('journal.edit_journal', self.journal))

    def test_knows_if_a_simple_user_cannot_edit_a_journal(self):
        # Setup
        user = User.objects.create_user(
            username='staff', email='admin@xyz.com', password='top_secret')
        # Run & check
        self.assertFalse(user.has_perm('journal.edit_journal'))
        self.assertFalse(user.has_perm('journal.edit_journal', self.journal))
