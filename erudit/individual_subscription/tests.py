from django.test import TestCase

from .factories import OrganizationPolicyFactory, IndividualAccountFactory


class OrganizationPolicyTestCase(TestCase):

    def test_total_accounts(self):
        policy = OrganizationPolicyFactory()
        IndividualAccountFactory(organization_policy=policy)
        IndividualAccountFactory(organization_policy=policy)
        self.assertEqual(policy.total_accounts, 2)

    def test_date_activation(self):
        policy = OrganizationPolicyFactory()
        self.assertIsNone(policy.date_activation)

        IndividualAccountFactory(organization_policy=policy)
        self.assertIsNotNone(policy.date_activation)

        first_date_activation = policy.date_activation
        IndividualAccountFactory(organization_policy=policy)
        self.assertEqual(policy.date_activation, first_date_activation)


class IndividualAccountTestCase(TestCase):

    def test_crypt_password(self):
        password = '123qwe'
        salt = 'nawak'
        php_script_result = 'H8HdFUyxvh8/ZxQ5SuF9E0W3SZ5uYXdhaw=='
        account = IndividualAccountFactory()
        self.assertEqual(account.sha1(password, salt), php_script_result)

    def test_default_password(self):
        account = IndividualAccountFactory()
        self.assertIsNotNone(account.password)

    def test_update_password(self):
        password = '123qwe'
        account = IndividualAccountFactory()
        old_password = account.password
        account.password = password
        account.save()
        self.assertNotEqual(account.password, password)
        self.assertNotEqual(account.password, old_password)

    def test_no_update_password(self):
        account = IndividualAccountFactory()
        password = account.password
        account.save()
        self.assertEqual(account.password, password)
