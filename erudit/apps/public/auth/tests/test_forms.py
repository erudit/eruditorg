# -*- coding: utf-8 -*-

from core.accounts.factories import AbonnementProfileFactory
from core.accounts.models import AbonnementProfile
from erudit.tests.base import BaseEruditTestCase

from ..forms import PasswordChangeForm


class TestPasswordChangeForm(BaseEruditTestCase):
    def test_can_change_the_new_password_of_a_standard_user(self):
        # Setup
        form_data = {
            'old_password': 'top_secret',
            'new_password1': 'not_secret',
            'new_password2': 'not_secret',
        }
        # Run & check
        form = PasswordChangeForm(self.user, form_data)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertTrue(self.user.has_usable_password())
        self.assertTrue(self.user.check_password('not_secret'))

    def test_can_change_the_new_password_of_an_abonnementprofile_user(self):
        # Setup
        self.user.set_unusable_password()
        self.user.save()
        profile = AbonnementProfileFactory.create(user=self.user)
        profile.password = profile.sha1('test-1')
        profile.save()
        form_data = {
            'old_password': 'test-1',
            'new_password1': 'not_secret',
            'new_password2': 'not_secret',
        }
        # Run & check
        form = PasswordChangeForm(self.user, form_data)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertTrue(self.user.has_usable_password())
        self.assertTrue(self.user.check_password('not_secret'))

    def test_can_remove_the_abonnementprofile_instance_associated_with_the_user(self):
        # Setup
        self.user.set_unusable_password()
        self.user.save()
        profile = AbonnementProfileFactory.create(user=self.user)
        profile.password = profile.sha1('test-1')
        profile.save()
        form_data = {
            'old_password': 'test-1',
            'new_password1': 'not_secret',
            'new_password2': 'not_secret',
        }
        # Run & check
        form = PasswordChangeForm(self.user, form_data)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertTrue(self.user.has_usable_password())
        self.assertTrue(self.user.check_password('not_secret'))
        self.assertFalse(AbonnementProfile.objects.exists())

    def test_raises_an_error_if_the_abonnementprofile_password_is_incorrect(self):
        # Setup
        self.user.set_unusable_password()
        self.user.save()
        profile = AbonnementProfileFactory.create(user=self.user)
        profile.password = profile.sha1('test-1')
        profile.save()
        form_data = {
            'old_password': 'dummy',
            'new_password1': 'not_secret',
            'new_password2': 'not_secret',
        }
        # Run & check
        form = PasswordChangeForm(self.user, form_data)
        self.assertFalse(form.is_valid())
        self.assertTrue('old_password' in form.errors)
