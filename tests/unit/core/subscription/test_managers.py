# -*- coding: utf-8 -*-

import datetime as dt

import pytest

from core.subscription.models import JournalAccessSubscription
from core.subscription.test.factories import JournalAccessSubscriptionFactory
from core.subscription.test.factories import JournalAccessSubscriptionPeriodFactory


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
