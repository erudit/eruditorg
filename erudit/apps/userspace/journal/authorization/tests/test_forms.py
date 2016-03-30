# -*- coding: utf-8 -*-

from core.authorization.defaults import AuthorizationConfig as AC
from core.authorization.models import Authorization
from erudit.tests.base import BaseEruditTestCase

from ..forms import AuthorizationForm


class TestAuthorizationForm(BaseEruditTestCase):
    def test_initializes_the_user_field_with_the_current_journal_members(self):
        # Run & check
        form = AuthorizationForm(
            codename=AC.can_manage_issuesubmission.codename, journal=self.journal)
        self.assertEqual(list(form.fields['user'].queryset), list(self.journal.members.all()))

    def test_can_validate_a_basic_authorization(self):
        # Setup
        form_data = {
            'user': self.user.id,
        }
        form = AuthorizationForm(
            form_data, codename=AC.can_manage_issuesubmission.codename, journal=self.journal)
        # Run & check
        self.assertTrue(form.is_valid())

    def test_can_save_a_basic_authorization(self):
        # Setup
        form_data = {
            'user': self.user.id,
        }
        form = AuthorizationForm(
            form_data, codename=AC.can_manage_issuesubmission.codename, journal=self.journal)
        # Run & check
        self.assertTrue(form.is_valid())
        form.save()
        authorization = Authorization.objects.first()
        self.assertEqual(authorization.user, self.user)
        self.assertEqual(authorization.content_object, self.journal)
        self.assertEqual(
            authorization.authorization_codename, AC.can_manage_issuesubmission.codename)
