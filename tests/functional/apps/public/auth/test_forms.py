# -*- coding: utf-8 -*-

from django.contrib.auth.tokens import default_token_generator
from django.core import mail

from erudit.test import BaseEruditTestCase

from apps.public.auth.forms import PasswordResetForm


class TestPasswordResetForm(BaseEruditTestCase):
    def test_can_properly_choose_standard_users_with_usable_passwords(self):
        # Setup
        self.user.email = 'foobar@example.com'
        self.user.save()
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
