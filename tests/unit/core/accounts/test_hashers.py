# -*- coding: utf-8 -*-

from django.contrib.auth.models import User

from base.test.testcases import EruditClientTestCase
from core.accounts.hashers import PBKDF2WrappedAbonnementsSHA1PasswordHasher


class TestPBKDF2WrappedAbonnementsSHA1PasswordHasher(EruditClientTestCase):
    def test_can_generate_usable_passwords_for_users(self):
        # Setup
        hasher = PBKDF2WrappedAbonnementsSHA1PasswordHasher()
        legacy_password = hasher.sha1('dummypassword')
        user = User.objects.create_user(username='dummy', email='dummy@xyz.com', password='void')
        user.password = hasher.encode_sha1_hash(legacy_password, hasher.salt())
        user.save()
        # Run & check
        assert self.client.login(username='dummy', password='dummypassword')

    def test_will_not_be_used_if_the_password_of_the_user_is_updated(self):
        # Setup
        hasher = PBKDF2WrappedAbonnementsSHA1PasswordHasher()
        legacy_password = hasher.sha1('dummypassword')
        user = User.objects.create_user(username='dummy', email='dummy@xyz.com', password='void')
        user.password = hasher.encode_sha1_hash(legacy_password, hasher.salt())
        user.save()
        user.set_password('newdummypassword')
        user.save()
        # Run & check
        assert self.client.login(username='dummy', password='newdummypassword')
        algorithm, _, _, _ = user.password.split('$')
        assert algorithm == 'pbkdf2_sha256'
