# -*- coding: utf-8 -*-

import datetime as dt

import pytest

from erudit.test.factories import CollectionFactory
from erudit.test.factories import JournalFactory
from erudit.test.factories import OrganisationFactory

from core.subscription.shortcuts import get_journal_organisation_subscribers
from core.subscription.test.factories import JournalAccessSubscriptionFactory
from core.subscription.test.factories import JournalAccessSubscriptionPeriodFactory


@pytest.mark.django_db
class TestGetJournalOrganisationSubscribers:
    def test_can_return_the_organisations_that_have_subscribed_to_a_journal(self):
        # Setup
        now_dt = dt.datetime.now()
        collection = CollectionFactory.create()
        journal = JournalFactory(collection=collection)
        org_1 = OrganisationFactory.create()
        org_2 = OrganisationFactory.create()
        org_3 = OrganisationFactory.create()
        OrganisationFactory.create()
        subscription_1 = JournalAccessSubscriptionFactory.create(
            organisation=org_1, journal=journal)
        JournalAccessSubscriptionPeriodFactory.create(
            subscription=subscription_1,
            start=now_dt - dt.timedelta(days=10),
            end=now_dt + dt.timedelta(days=8))
        subscription_2 = JournalAccessSubscriptionFactory.create(
            organisation=org_2, collection=journal.collection)
        JournalAccessSubscriptionPeriodFactory.create(
            subscription=subscription_2,
            start=now_dt - dt.timedelta(days=10),
            end=now_dt + dt.timedelta(days=8))
        subscription_3 = JournalAccessSubscriptionFactory.create(organisation=org_3)
        subscription_3.journals.add(journal)
        JournalAccessSubscriptionPeriodFactory.create(
            subscription=subscription_3,
            start=now_dt - dt.timedelta(days=10),
            end=now_dt + dt.timedelta(days=8))
        # Run & check
        assert set(get_journal_organisation_subscribers(journal)) == set([org_1, org_2, org_3, ])

    def test_cannot_return_organisations_with_non_ongoing_subscriptions(self):
        # Setup
        now_dt = dt.datetime.now()
        collection = CollectionFactory.create()
        journal = JournalFactory(collection=collection)
        org_1 = OrganisationFactory.create()
        org_2 = OrganisationFactory.create()
        org_3 = OrganisationFactory.create()
        OrganisationFactory.create()
        subscription_1 = JournalAccessSubscriptionFactory.create(
            organisation=org_1, journal=journal)
        JournalAccessSubscriptionPeriodFactory.create(
            subscription=subscription_1,
            start=now_dt - dt.timedelta(days=10),
            end=now_dt + dt.timedelta(days=8))
        subscription_2 = JournalAccessSubscriptionFactory.create(
            organisation=org_2, collection=journal.collection)
        JournalAccessSubscriptionPeriodFactory.create(
            subscription=subscription_2,
            start=now_dt - dt.timedelta(days=10),
            end=now_dt - dt.timedelta(days=5))
        subscription_3 = JournalAccessSubscriptionFactory.create(organisation=org_3)
        subscription_3.journals.add(journal)
        JournalAccessSubscriptionPeriodFactory.create(
            subscription=subscription_3,
            start=now_dt - dt.timedelta(days=10),
            end=now_dt + dt.timedelta(days=8))
        # Run & check
        assert set(get_journal_organisation_subscribers(journal)) == set([org_1, org_3, ])
