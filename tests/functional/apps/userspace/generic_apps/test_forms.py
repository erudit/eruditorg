from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from base.test.factories import UserFactory
from erudit.test.factories import JournalFactory
from core.authorization.defaults import AuthorizationConfig as AC
from core.authorization.models import Authorization

from apps.userspace.generic_apps.authorization.forms import AuthorizationForm


class TestAuthorizationForm(TestCase):
    def test_initializes_the_user_field_with_the_current_journal_members(self):
        journal = JournalFactory()
        form = AuthorizationForm(codename=AC.can_manage_issuesubmission.codename, target=journal)
        self.assertEqual(list(form.fields["user"].queryset), list(journal.members.all()))

    def test_can_validate_a_basic_authorization(self):
        user = UserFactory()
        journal = JournalFactory()
        journal.members.add(user)
        form_data = {
            "user": user.id,
        }
        form = AuthorizationForm(
            form_data, codename=AC.can_manage_issuesubmission.codename, target=journal
        )
        self.assertTrue(form.is_valid())

    def test_can_save_a_basic_authorization(self):
        user = UserFactory()
        journal = JournalFactory()
        journal.members.add(user)
        form_data = {
            "user": user.id,
        }
        form = AuthorizationForm(
            form_data, codename=AC.can_manage_issuesubmission.codename, target=journal
        )
        self.assertTrue(form.is_valid())
        form.save()
        authorization = Authorization.objects.first()
        self.assertEqual(authorization.user, user)
        self.assertEqual(authorization.content_object, journal)
        self.assertEqual(
            authorization.authorization_codename, AC.can_manage_issuesubmission.codename
        )

    def test_do_not_allow_to_create_an_authorization_for_a_user_that_is_already_authorized(self):
        user = UserFactory()
        journal = JournalFactory()
        journal.members.add(user)
        ct = ContentType.objects.get(app_label="erudit", model="journal")
        Authorization.objects.create(
            content_type=ct,
            user=user,
            object_id=journal.id,
            authorization_codename=AC.can_manage_issuesubmission.codename,
        )
        form_data = {
            "user": user.id,
        }
        form = AuthorizationForm(
            form_data, codename=AC.can_manage_issuesubmission.codename, target=journal
        )
        self.assertFalse(form.is_valid())
        self.assertTrue("user" in form.errors)
