from unittest import mock

from django.test import TestCase, override_settings
from django.contrib.auth.models import User

from base.backends import MandragoreBackend


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
    @mock.patch('base.backends.get_user_from_mandragore', new=mock.MagicMock(
        return_value=('test_user', '$6$salt$passwd')))
    def test_authentication_success(self):

        with mock.patch('crypt.crypt', new=mock.MagicMock(return_value='$6$salt$passwd')):
            user = self.backend.authenticate(
                username='test_user', password='test_password'
            )

            self.assertEqual(user, self.user)

    @override_settings(EXTERNAL_DATABASES={'mandragore': 'dummy'})
    @mock.patch('base.backends.get_user_from_mandragore', new=mock.MagicMock(
        return_value=('test_user', '$6$salt$passwd')))
    def test_wrong_password(self):
        user = self.backend.authenticate(
            username='test_user', password='wrong_password'
        )

        self.assertIsNone(user)
