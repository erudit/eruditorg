# -*- coding: utf-8 -*-

from django.contrib.contenttypes.models import ContentType

from core.authorization.defaults import AuthorizationConfig as AC
from core.authorization.models import Authorization
from erudit.tests.base import BaseEruditTestCase

from ..forms import AuthorizationForm


class TestAuthorizationForm(BaseEruditTestCase):
    def test_initializes_the_user_field_with_the_current_journal_members(self):
        # Run & check
        form = AuthorizationForm(
            codename=AC.can_manage_issuesubmission.codename, target=self.journal)
        self.assertEqual(list(form.fields['user'].queryset), list(self.journal.members.all()))

    def test_can_validate_a_basic_authorization(self):
        # Setup
        form_data = {
            'user': self.user.id,
        }
        form = AuthorizationForm(
            form_data, codename=AC.can_manage_issuesubmission.codename, target=self.journal)
        # Run & check
        self.assertTrue(form.is_valid())

    def test_can_save_a_basic_authorization(self):
        # Setup
        form_data = {
            'user': self.user.id,
        }
        form = AuthorizationForm(
            form_data, codename=AC.can_manage_issuesubmission.codename, target=self.journal)
        # Run & check
        self.assertTrue(form.is_valid())
        form.save()
        authorization = Authorization.objects.first()
        self.assertEqual(authorization.user, self.user)
        self.assertEqual(authorization.content_object, self.journal)
        self.assertEqual(
            authorization.authorization_codename, AC.can_manage_issuesubmission.codename)

    def test_do_not_allow_to_create_an_authorization_for_a_user_that_is_already_authorized(self):
        # Setup
        ct = ContentType.objects.get(app_label="erudit", model="journal")
        Authorization.objects.create(
            content_type=ct,
            user=self.user,
            object_id=self.journal.id,
            authorization_codename=AC.can_manage_issuesubmission.codename)
        form_data = {
            'user': self.user.id,
        }
        form = AuthorizationForm(
            form_data, codename=AC.can_manage_issuesubmission.codename, target=self.journal)
        # Run & check
        self.assertFalse(form.is_valid())
        self.assertTrue('user' in form.errors)
