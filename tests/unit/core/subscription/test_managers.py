import pytest

from core.subscription.models import JournalAccessSubscription
from core.subscription.test.factories import (
    JournalAccessSubscriptionFactory,
    JournalManagementSubscriptionFactory,
)
from core.subscription.test.factories import InstitutionIPAddressRangeFactory

pytestmark = pytest.mark.django_db


def test_valid_objects_filters_valid_subscriptions():
    valid_jms = JournalManagementSubscriptionFactory()
    valid_accesses = [
        # Institutional subscriptions need a valid period.
        JournalAccessSubscriptionFactory(type="institutional", post__valid=True),
        # Individual subscriptions need a journal with an active management plan, but it doesn't
        # need an active period on the subscription itself.
        JournalAccessSubscriptionFactory(
            type="individual", journal_management_subscription=valid_jms, post__valid=True
        ),
        JournalAccessSubscriptionFactory(
            type="individual", journal_management_subscription=valid_jms, post__valid=True
        ),
    ]

    assert list(JournalAccessSubscription.valid_objects.all()) == valid_accesses
    assert list(JournalAccessSubscription.valid_objects.institutional()) == valid_accesses[:1]
    assert list(JournalAccessSubscription.valid_objects.individual()) == valid_accesses[1:]


def test_can_return_subscriptions_for_an_ip_covered_by_multiple_ranges():
    subscription = JournalAccessSubscriptionFactory(post__valid=True)

    InstitutionIPAddressRangeFactory.create(
        subscription=subscription,
        ip_start="192.168.1.1",
        ip_end="192.168.1.2",
    )

    InstitutionIPAddressRangeFactory.create(
        subscription=subscription,
        ip_start="192.168.1.1",
        ip_end="192.168.1.2",
    )

    assert list(JournalAccessSubscription.valid_objects.get_for_ip_address("192.168.1.1")) == [
        subscription
    ]


def test_can_return_subscriptions_for_an_ip():
    subscription = JournalAccessSubscriptionFactory(post__valid=True)

    InstitutionIPAddressRangeFactory.create(
        subscription=subscription,
        ip_start="192.168.1.1",
        ip_end="192.168.1.2",
    )

    assert list(JournalAccessSubscription.valid_objects.get_for_ip_address("192.168.1.1")) == [
        subscription
    ]
