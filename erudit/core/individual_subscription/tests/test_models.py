from django.test import TestCase

from erudit.factories import JournalFactory
from erudit.models import Journal

from ..factories import PolicyFactory, IndividualAccountFactory
from ..models import IndividualAccountJournal, PolicyEvent


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


class IndividualAccountJournalTestCase(TestCase):

    def test_run_command_twice(self):
        policy = PolicyFactory()
        IndividualAccountFactory(policy=policy)
        IndividualAccountFactory(policy=policy)
        JournalFactory.create_batch(10)
        policy.access_full = True
        policy.save()
        policy.generate_flat_access()
        self.assertEqual(IndividualAccountJournal.objects.count(), 20)
        policy.generate_flat_access()
        self.assertEqual(IndividualAccountJournal.objects.count(), 20)

    def test_removed_account(self):
        policy = PolicyFactory()
        dude_to_delete = IndividualAccountFactory(policy=policy)
        IndividualAccountFactory(policy=policy)
        JournalFactory.create_batch(10)
        policy.access_full = True
        policy.save()
        policy.generate_flat_access()
        dude_to_delete.delete()
        self.assertEqual(IndividualAccountJournal.objects.count(), 10)

    def test_removed_journal(self):
        policy = PolicyFactory()
        IndividualAccountFactory(policy=policy)
        IndividualAccountFactory(policy=policy)
        JournalFactory.create_batch(10)
        policy.access_full = True
        policy.save()
        policy.generate_flat_access()
        Journal.objects.first().delete()
        self.assertEqual(IndividualAccountJournal.objects.count(), 18)


class IndividualAccountJournalFullAccessTestCase(TestCase):

    def test_add_full_access(self):
        policy = PolicyFactory()
        IndividualAccountFactory(policy=policy)
        IndividualAccountFactory(policy=policy)
        JournalFactory.create_batch(10)
        policy.access_full = True
        policy.save()
        policy.generate_flat_access()
        self.assertEqual(IndividualAccountJournal.objects.count(), 20)


class IndividualAccountJournalCustomTestCase(TestCase):

    def test_link_journals(self):
        policy = PolicyFactory()
        policy.access_journal = JournalFactory.create_batch(2)
        policy.save()
        IndividualAccountFactory(policy=policy)
        IndividualAccountFactory(policy=policy)
        policy.generate_flat_access()
        self.assertEqual(IndividualAccountJournal.objects.count(), 4)

    def test_remove_account(self):
        policy = PolicyFactory()
        policy.access_journal = JournalFactory.create_batch(2)
        policy.save()
        dude_to_delete = IndividualAccountFactory(policy=policy)
        IndividualAccountFactory(policy=policy)
        policy.generate_flat_access()
        dude_to_delete.delete()
        policy.generate_flat_access()
        self.assertEqual(IndividualAccountJournal.objects.count(), 2)


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
