# -*- coding: utf-8 -*-

import ipaddress

from django.core.exceptions import ValidationError
from django.test import TestCase

from erudit.factories import OrganisationFactory

from ..factories import (
    PolicyFactory, IndividualAccountFactory,
    InstitutionalAccountFactory, InstitutionIPAddressRangeFactory
)
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


class TestInstitutionIPAddressRange(TestCase):
    def setUp(self):
        self.policy = PolicyFactory.create(max_accounts=2)
        self.organisation = OrganisationFactory.create()
        self.institutional_account = InstitutionalAccountFactory(
            institution=self.organisation, )

    def test_cannot_be_saved_with_an_incoherent_ip_range(self):
        # Run & check
        with self.assertRaises(ValidationError):
            ip_range = InstitutionIPAddressRangeFactory.build(
                institutional_account=self.institutional_account,
                ip_start='192.168.1.3', ip_end='192.168.1.2')
            ip_range.clean()

    def test_can_return_the_list_of_corresponding_ip_addresses(self):
        # Setup
        ip_range = InstitutionIPAddressRangeFactory.build(
            institutional_account=self.institutional_account,
            ip_start='192.168.1.3', ip_end='192.168.1.5')
        # Run
        ip_addresses = ip_range.ip_addresses
        # Check
        self.assertEqual(
            ip_addresses, [
                ipaddress.ip_address('192.168.1.3'),
                ipaddress.ip_address('192.168.1.4'),
                ipaddress.ip_address('192.168.1.5'),
            ]
        )
