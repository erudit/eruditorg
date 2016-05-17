# -*- coding: utf-8 -*-

import datetime as dt
import ipaddress

from django.core.exceptions import ValidationError
from django.test import TestCase

from erudit.factories import OrganisationFactory
from erudit.tests.base import BaseEruditTestCase

from ..factories import InstitutionIPAddressRangeFactory
from ..factories import JournalAccessSubscriptionFactory
from ..factories import JournalAccessSubscriptionPeriodFactory
from ..factories import JournalManagementPlanFactory
from ..factories import JournalManagementSubscriptionFactory
from ..factories import JournalManagementSubscriptionPeriodFactory


class TestJournalAccessSubscription(TestCase):
    def test_knows_if_it_is_ongoing_or_not(self):
        # Setup
        now_dt = dt.datetime.now()
        subscription_1 = JournalAccessSubscriptionFactory.create()
        subscription_2 = JournalAccessSubscriptionFactory.create()
        JournalAccessSubscriptionPeriodFactory.create(
            subscription=subscription_1,
            start=now_dt - dt.timedelta(days=10),
            end=now_dt + dt.timedelta(days=8))
        JournalAccessSubscriptionPeriodFactory.create(
            subscription=subscription_2,
            start=now_dt + dt.timedelta(days=10),
            end=now_dt + dt.timedelta(days=8))
        # Run & check
        self.assertTrue(subscription_1.is_ongoing)
        self.assertFalse(subscription_2.is_ongoing)


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


class TestJournalAccessSubscriptionPeriod(TestCase):
    def test_cannot_clean_an_incoherent_period(self):
        # Setup
        now_dt = dt.datetime.now()
        subscription = JournalAccessSubscriptionFactory.create()
        period = JournalAccessSubscriptionPeriodFactory.build(
            subscription=subscription,
            start=now_dt + dt.timedelta(days=10),
            end=now_dt + dt.timedelta(days=8))
        # Run & check
        with self.assertRaises(ValidationError):
            period.clean()

    def test_cannot_clean_a_period_that_has_a_larger_concurrent_period(self):
        # Setup
        now_dt = dt.datetime.now()
        subscription = JournalAccessSubscriptionFactory.create()
        JournalAccessSubscriptionPeriodFactory.create(
            subscription=subscription,
            start=now_dt + dt.timedelta(days=8),
            end=now_dt + dt.timedelta(days=14))
        period = JournalAccessSubscriptionPeriodFactory.build(
            subscription=subscription,
            start=now_dt + dt.timedelta(days=10),
            end=now_dt + dt.timedelta(days=12))
        # Run & check
        with self.assertRaises(ValidationError):
            period.clean()

    def test_cannot_clean_a_period_that_has_an_inner_concurrent_period(self):
        # Setup
        now_dt = dt.datetime.now()
        subscription = JournalAccessSubscriptionFactory.create()
        JournalAccessSubscriptionPeriodFactory.create(
            subscription=subscription,
            start=now_dt + dt.timedelta(days=9),
            end=now_dt + dt.timedelta(days=11))
        period = JournalAccessSubscriptionPeriodFactory.build(
            subscription=subscription,
            start=now_dt + dt.timedelta(days=8),
            end=now_dt + dt.timedelta(days=14))
        # Run & check
        with self.assertRaises(ValidationError):
            period.clean()

    def test_cannot_clean_a_period_that_has_an_older_concurrent_period(self):
        # Setup
        now_dt = dt.datetime.now()
        subscription = JournalAccessSubscriptionFactory.create()
        JournalAccessSubscriptionPeriodFactory.create(
            subscription=subscription,
            start=now_dt + dt.timedelta(days=8),
            end=now_dt + dt.timedelta(days=11))
        period = JournalAccessSubscriptionPeriodFactory.build(
            subscription=subscription,
            start=now_dt + dt.timedelta(days=10),
            end=now_dt + dt.timedelta(days=12))
        # Run & check
        with self.assertRaises(ValidationError):
            period.clean()

    def test_cannot_clean_a_period_that_has_a_younger_concurrent_period(self):
        # Setup
        now_dt = dt.datetime.now()
        subscription = JournalAccessSubscriptionFactory.create()
        JournalAccessSubscriptionPeriodFactory.create(
            subscription=subscription,
            start=now_dt + dt.timedelta(days=11),
            end=now_dt + dt.timedelta(days=15))
        period = JournalAccessSubscriptionPeriodFactory.build(
            subscription=subscription,
            start=now_dt + dt.timedelta(days=10),
            end=now_dt + dt.timedelta(days=12))
        # Run & check
        with self.assertRaises(ValidationError):
            period.clean()


class TestJournalManagementSubscription(BaseEruditTestCase):
    def test_knows_if_it_is_ongoing_or_not(self):
        # Setup
        now_dt = dt.datetime.now()
        plan = JournalManagementPlanFactory.create(max_accounts=10)
        subscription_1 = JournalManagementSubscriptionFactory.create(
            journal=self.journal, plan=plan)
        subscription_2 = JournalManagementSubscriptionFactory.create(
            journal=self.journal, plan=plan)
        JournalManagementSubscriptionPeriodFactory.create(
            subscription=subscription_1,
            start=now_dt - dt.timedelta(days=10),
            end=now_dt + dt.timedelta(days=8))
        JournalManagementSubscriptionPeriodFactory.create(
            subscription=subscription_2,
            start=now_dt + dt.timedelta(days=10),
            end=now_dt + dt.timedelta(days=8))
        # Run & check
        self.assertTrue(subscription_1.is_ongoing)
        self.assertFalse(subscription_2.is_ongoing)
