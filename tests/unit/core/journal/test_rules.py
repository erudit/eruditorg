from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from base.test.factories import UserFactory
from erudit.test.factories import JournalFactory
from core.authorization.defaults import AuthorizationConfig as AC
from core.authorization.test.factories import AuthorizationFactory


class TestEditJournalRule(TestCase):
    def test_knows_that_a_superuser_can_edit_journal_information(self):
        # Setup
        user = User.objects.create_superuser(
            username="admin", email="admin@xyz.com", password="top_secret"
        )
        journal = JournalFactory()
        journal.members.add(user)
        # Run & check
        self.assertTrue(user.has_perm("journal.edit_journal_information"))
        self.assertTrue(user.has_perm("journal.edit_journal_information", journal))

    def test_knows_that_a_staff_member_can_edit_journal_information(self):
        # Setup
        user = User.objects.create_user(
            username="staff", email="admin@xyz.com", password="top_secret"
        )
        user.is_staff = True
        user.save()
        journal = JournalFactory()
        journal.members.add(user)
        # Run & check
        self.assertTrue(user.has_perm("journal.edit_journal_information"))
        self.assertTrue(user.has_perm("journal.edit_journal_information", journal))

    def test_knows_if_a_simple_user_can_edit_journal_information(self):
        # Setup
        user = UserFactory.create()
        journal = JournalFactory()
        journal.members.add(user)
        AuthorizationFactory.create(
            content_type=ContentType.objects.get_for_model(journal),
            object_id=journal.id,
            user=user,
            authorization_codename=AC.can_edit_journal_information.codename,
        )
        # Run & check
        self.assertTrue(user.has_perm("journal.edit_journal_information"))
        self.assertTrue(user.has_perm("journal.edit_journal_information", journal))

    def test_knows_if_a_simple_user_cannot_edit_journal_information(self):
        # Setup
        journal = JournalFactory()
        user = User.objects.create_user(
            username="staff", email="admin@xyz.com", password="top_secret"
        )
        # Run & check
        self.assertFalse(user.has_perm("journal.edit_journal_information"))
        self.assertFalse(user.has_perm("journal.edit_journal_information", journal))
