# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from core.authorization.defaults import AuthorizationConfig as AC
from core.authorization.factories import AuthorizationFactory
from erudit.tests import BaseEruditTestCase


class TestEditJournalRule(BaseEruditTestCase):
    def test_knows_that_a_superuser_can_edit_journal_information(self):
        # Setup
        user = User.objects.create_superuser(
            username='admin', email='admin@xyz.com', password='top_secret')
        # Run & check
        self.assertTrue(user.has_perm('journal.edit_journal_information'))
        self.assertTrue(user.has_perm('journal.edit_journal_information', self.journal))

    def test_knows_that_a_staff_member_can_edit_journal_information(self):
        # Setup
        user = User.objects.create_user(
            username='staff', email='admin@xyz.com', password='top_secret')
        user.is_staff = True
        user.save()
        # Run & check
        self.assertTrue(user.has_perm('journal.edit_journal_information'))
        self.assertTrue(user.has_perm('journal.edit_journal_information', self.journal))

    def test_knows_if_a_simple_user_can_edit_journal_information(self):
        # Setup
        AuthorizationFactory.create(
            content_type=ContentType.objects.get_for_model(self.journal), object_id=self.journal.id,
            user=self.user, authorization_codename=AC.can_edit_journal_information.codename)
        # Run & check
        self.assertTrue(self.user.has_perm('journal.edit_journal_information'))
        self.assertTrue(self.user.has_perm('journal.edit_journal_information', self.journal))

    def test_knows_if_a_simple_user_cannot_edit_journal_information(self):
        # Setup
        user = User.objects.create_user(
            username='staff', email='admin@xyz.com', password='top_secret')
        # Run & check
        self.assertFalse(user.has_perm('journal.edit_journal_information'))
        self.assertFalse(user.has_perm('journal.edit_journal_information', self.journal))
