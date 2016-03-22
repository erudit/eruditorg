# -*- coding: utf-8 -*-

import ipaddress

from django.core.exceptions import ValidationError
from django.test import TestCase

from erudit.factories import OrganisationFactory

from ..factories import InstitutionIPAddressRangeFactory
from ..factories import JournalAccessSubscriptionFactory


class TestInstitutionIPAddressRange(TestCase):
    def setUp(self):
        self.organisation = OrganisationFactory.create()
        self.subscription = JournalAccessSubscriptionFactory(organisation=self.organisation)

    def test_cannot_be_saved_with_an_incoherent_ip_range(self):
        # Run & check
        with self.assertRaises(ValidationError):
            ip_range = InstitutionIPAddressRangeFactory.build(
                subscription=self.subscription,
                ip_start='192.168.1.3', ip_end='192.168.1.2')
            ip_range.clean()

    def test_can_return_the_list_of_corresponding_ip_addresses(self):
        # Setup
        ip_range = InstitutionIPAddressRangeFactory.build(
            subscription=self.subscription,
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
