# -*- coding: utf-8 -*-

import datetime as dt

import pytest

from core.subscription.models import JournalAccessSubscription
from core.subscription.test.factories import (
    JournalAccessSubscriptionFactory,
    ValidJournalAccessSubscriptionPeriodFactory
)
from core.subscription.test.factories import JournalAccessSubscriptionPeriodFactory
from core.subscription.test.factories import InstitutionIPAddressRangeFactory


@pytest.mark.django_db
class TestJournalAccessSubscriptionValidManager(object):
    def test_can_return_only_the_valid_subscriptions(self):
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
        assert list(JournalAccessSubscription.valid_objects.all()) == [subscription_1, ]

    def test_can_return_subscriptions_for_an_ip(self):

        subscription_period = ValidJournalAccessSubscriptionPeriodFactory.create()

        InstitutionIPAddressRangeFactory.create(
            subscription=subscription_period.subscription,
            ip_start='192.168.1.1',
            ip_end='192.168.1.2',
        )

        assert list(JournalAccessSubscription.valid_objects.get_for_ip_address('192.168.1.1')) == [subscription_period.subscription]

        subscription_period = ValidJournalAccessSubscriptionPeriodFactory.create()

        InstitutionIPAddressRangeFactory.create(
            subscription=subscription_period.subscription,
            ip_start='192.168.1.1',
            ip_end='192.168.255.255',
        )

        assert list(JournalAccessSubscription.valid_objects.get_for_ip_address('192.168.70.1')) == [subscription_period.subscription]
