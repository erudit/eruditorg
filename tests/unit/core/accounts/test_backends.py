from django.contrib.auth.models import User
from django.test import TestCase

from core.accounts.backends import EmailBackend


class TestEmailBackend(TestCase):
    def test_can_authenticate_a_user_using_his_username(self):
        # Setup
        user = User.objects.create_user(
            username="test_user", email="david.cormier@erudit.org", password="test_password"
        )
        backend = EmailBackend()
        # Run & check
        self.assertEqual(
            backend.authenticate(None, username="test_user", password="test_password"), user
        )

    def test_can_authenticate_a_user_using_his_email_address(self):
        # Setup
        user = User.objects.create_user(
            username="test_user", email="david.cormier@erudit.org", password="test_password"
        )
        backend = EmailBackend()
        # Run & check
        self.assertEqual(
            backend.authenticate(
                None, username="david.cormier@erudit.org", password="test_password"
            ),
            user,
        )

    def test_can_properly_handle_an_invalid_username(self):
        # Setup
        User.objects.create_user(
            username="test_user", email="david.cormier@erudit.org", password="test_password"
        )
        backend = EmailBackend()
        # Run & check
        self.assertIsNone(backend.authenticate(None, username="test_u", password="test_password"))

    def test_can_properly_handle_an_invalid_email_address(self):
        # Setup
        User.objects.create_user(
            username="test_user", email="david.cormier@erudit.org", password="test_password"
        )
        backend = EmailBackend()
        # Run & check
        self.assertIsNone(
            backend.authenticate(None, username="foobar@erudit.org", password="test_password")
        )

    def test_can_properly_handle_an_invalid_password(self):
        # Setup
        User.objects.create_user(
            username="test_user", email="david.cormier@erudit.org", password="test_password"
        )
        backend = EmailBackend()
        # Run & check
        self.assertIsNone(
            backend.authenticate(None, username="david.cormier@erudit.org", password="bad_password")
        )

    def test_can_properly_handle_multiple_users_with_the_same_email_address(self):
        # Setup
        User.objects.create_user(
            username="test_user_1", email="david.cormier@erudit.org", password="test_password"
        )
        User.objects.create_user(
            username="test_user_2", email="david.cormier@erudit.org", password="test_password"
        )
        backend = EmailBackend()
        # Run & check
        self.assertIsNone(
            backend.authenticate(
                None, username="david.cormier@erudit.org", password="test_password"
            )
        )
