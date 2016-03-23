# -*- coding: utf-8 -*-

from django.test import TestCase

from ..factories import AbonnementProfileFactory


class IndividualAccountTestCase(TestCase):

    def test_crypt_password(self):
        password = '123qwe'
        salt = 'nawak'
        php_script_result = 'H8HdFUyxvh8/ZxQ5SuF9E0W3SZ5uYXdhaw=='
        account = AbonnementProfileFactory()
        self.assertEqual(account.sha1(password, salt), php_script_result)

    def test_default_password(self):
        account = AbonnementProfileFactory()
        self.assertIsNotNone(account.password)

    def test_update_password(self):
        password = '123qwe'
        account = AbonnementProfileFactory()
        old_password = account.password
        account.password = password
        account.save()
        self.assertNotEqual(account.password, password)
        self.assertNotEqual(account.password, old_password)

    def test_no_update_password(self):
        account = AbonnementProfileFactory()
        password = account.password
        account.save()
        self.assertEqual(account.password, password)
