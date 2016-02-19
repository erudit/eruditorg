from django.test import TestCase

from ..factories import PolicyFactory, IndividualAccountFactory
from ..models import PolicyEvent


class OrganizationPolicyTestCase(TestCase):

    def test_total_accounts(self):
        policy = PolicyFactory()
        IndividualAccountFactory(policy=policy)
        IndividualAccountFactory(policy=policy)
        self.assertEqual(policy.total_accounts, 2)

    def test_date_activation(self):
        policy = PolicyFactory()
        self.assertIsNone(policy.date_activation)

        IndividualAccountFactory(policy=policy)
        self.assertIsNotNone(policy.date_activation)

        first_date_activation = policy.date_activation
        IndividualAccountFactory(policy=policy)
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


class EventTestCase(TestCase):

    def test_event_with_no_pb(self):
        policy = PolicyFactory(max_accounts=2)
        policy.save()
        IndividualAccountFactory(policy=policy)
        IndividualAccountFactory(policy=policy)
        policy.notify_limit_reached()
        self.assertEqual(PolicyEvent.objects.count(), 0)

    def test_over(self):
        policy = PolicyFactory(max_accounts=1)
        policy.save()
        IndividualAccountFactory(policy=policy)
        IndividualAccountFactory(policy=policy)
        policy.notify_limit_reached()
        self.assertEqual(PolicyEvent.objects.count(), 1)

    def test_no_spam_event(self):
        policy = PolicyFactory(max_accounts=1)
        policy.save()
        IndividualAccountFactory(policy=policy)
        IndividualAccountFactory(policy=policy)
        policy.notify_limit_reached()
        policy.notify_limit_reached()
        self.assertEqual(PolicyEvent.objects.count(), 1)
