# -*- coding: utf-8 -*-

from unittest import mock

from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from core.accounts.backends import EmailBackend
from core.accounts.backends import MandragoreBackend


class TestEmailBackend(TestCase):
    def test_can_authenticate_a_user_using_his_username(self):
        # Setup
        user = User.objects.create_user(
            username='test_user', email='david.cormier@erudit.org', password='test_password')
        backend = EmailBackend()
        # Run & check
        self.assertEqual(
            backend.authenticate(username='test_user', password='test_password'), user)

    def test_can_authenticate_a_user_using_his_email_address(self):
        # Setup
        user = User.objects.create_user(
            username='test_user', email='david.cormier@erudit.org', password='test_password')
        backend = EmailBackend()
        # Run & check
        self.assertEqual(
            backend.authenticate(username='david.cormier@erudit.org', password='test_password'),
            user)

    def test_can_properly_handle_an_invalid_username(self):
        # Setup
        User.objects.create_user(
            username='test_user', email='david.cormier@erudit.org', password='test_password')
        backend = EmailBackend()
        # Run & check
        self.assertIsNone(backend.authenticate(username='test_u', password='test_password'))

    def test_can_properly_handle_an_invalid_email_address(self):
        # Setup
        User.objects.create_user(
            username='test_user', email='david.cormier@erudit.org', password='test_password')
        backend = EmailBackend()
        # Run & check
        self.assertIsNone(
            backend.authenticate(username='foobar@erudit.org', password='test_password'))

    def test_can_properly_handle_an_invalid_password(self):
        # Setup
        User.objects.create_user(
            username='test_user', email='david.cormier@erudit.org', password='test_password')
        backend = EmailBackend()
        # Run & check
        self.assertIsNone(
            backend.authenticate(username='david.cormier@erudit.org', password='bad_password'))

    def test_can_properly_handle_multiple_users_with_the_same_email_address(self):
        # Setup
        User.objects.create_user(
            username='test_user_1', email='david.cormier@erudit.org', password='test_password')
        User.objects.create_user(
            username='test_user_2', email='david.cormier@erudit.org', password='test_password')
        backend = EmailBackend()
        # Run & check
        self.assertIsNone(
            backend.authenticate(username='david.cormier@erudit.org', password='test_password'))


class MandragoreBackendTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='test_user',
            email='david.cormier@erudit.org',
            password='test_password'
        )

        self.backend = MandragoreBackend()

    def test_invalid_username(self):
        user = self.backend.authenticate(
            username='test_wrong_username', password='test_password'
        )
        self.assertIsNone(user)

    def test_no_externaldb_in_settings(self):
        with self.settings(EXTERNAL_DATABASES=None):
            user = self.backend.authenticate(
                username='test_user', password='test_password'
            )

            self.assertIsNone(user)

    def test_no_mandragore_in_externaldb_settings(self):
        with self.settings(EXTERNAL_DATABASES={}):
            user = self.backend.authenticate(
                username='test_user', password='test_password'
            )
            self.assertIsNone(user)

    @override_settings(EXTERNAL_DATABASES={'mandragore': 'dummy'})
    @mock.patch('core.accounts.backends.get_user_from_mandragore', new=mock.MagicMock(
        return_value=('test_user', '$6$salt$passwd')))
    def test_authentication_success(self):

        with mock.patch('crypt.crypt', new=mock.MagicMock(return_value='$6$salt$passwd')):
            user = self.backend.authenticate(
                username='test_user', password='test_password'
            )

            self.assertEqual(user, self.user)

    @override_settings(EXTERNAL_DATABASES={'mandragore': 'dummy'})
    @mock.patch('core.accounts.backends.get_user_from_mandragore', new=mock.MagicMock(
        return_value=('test_user', '$6$salt$passwd')))
    def test_wrong_password(self):
        user = self.backend.authenticate(
            username='test_user', password='wrong_password'
        )

        self.assertIsNone(user)
