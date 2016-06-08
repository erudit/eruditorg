# -*- coding: utf-8 -*-

from django.contrib.auth.tokens import default_token_generator
from django.core import mail

from erudit.test import BaseEruditTestCase

from core.accounts.models import AbonnementProfile
from core.accounts.test.factories import AbonnementProfileFactory

from apps.public.auth.forms import PasswordChangeForm
from apps.public.auth.forms import PasswordResetForm


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


class TestPasswordResetForm(BaseEruditTestCase):
    def test_can_properly_choose_standard_users_with_usable_passwords(self):
        # Setup
        self.user.email = 'foobar@example.com'
        self.user.save()
        # Run & check
        form = PasswordResetForm({})
        self.assertEqual(list(form.get_users('foobar@example.com')), [self.user, ])

    def test_can_properly_choose_abonnementprofile_users_without_usable_passwords(self):
        # Setup
        self.user.set_unusable_password()
        self.user.email = 'foobar@example.com'
        self.user.save()
        profile = AbonnementProfileFactory.create(user=self.user)
        profile.password = profile.sha1('test-1')
        profile.save()
        # Run & check
        form = PasswordResetForm({})
        self.assertEqual(list(form.get_users('foobar@example.com')), [self.user, ])

    def test_cannot_choose_users_without_usable_passwords(self):
        # Setup
        self.user.set_unusable_password()
        self.user.email = 'foobar@example.com'
        self.user.save()
        # Run & check
        form = PasswordResetForm({})
        self.assertFalse(len(list(form.get_users('foobar@example.com'))))

    def test_can_properly_send_the_reset_email(self):
        # Setup
        self.user.email = 'foobar@example.com'
        self.user.save()
        form_data = {
            'email': 'foobar@example.com',
        }
        # Run & check
        form = PasswordResetForm(form_data)
        self.assertTrue(form.is_valid())
        form.save(
            domain_override=None,
            subject_template_name='emails/auth/password_reset_subject.txt',
            email_template_name='emails/auth/password_reset_email.html',
            use_https=False, token_generator=default_token_generator,
            from_email=None, request=None, html_email_template_name=None)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], 'foobar@example.com')
