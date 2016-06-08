# -*- coding: utf-8 -*-

import datetime as dt

from django.contrib.auth.models import AnonymousUser

from erudit.test import BaseEruditTestCase
from erudit.test.factories import OrganisationFactory

from base.test.factories import UserFactory
from core.subscription.test.factories import JournalAccessSubscriptionFactory
from core.subscription.test.factories import JournalAccessSubscriptionPeriodFactory

from apps.userspace.library.shortcuts import get_managed_organisations


class TestGetManagedOrganisationsShortcut(BaseEruditTestCase):
    def test_cannot_return_managed_organisations_for_anonymous_users(self):
        # Setup
        OrganisationFactory.create()
        user = AnonymousUser()
        # Run & check
        self.assertIsNone(get_managed_organisations(user))

    def test_return_all_organisations_for_superusers_and_staff_users(self):
        # Setup
        org_1 = OrganisationFactory.create()
        org_2 = OrganisationFactory.create()
        user_1 = UserFactory.create(is_superuser=True)
        user_2 = UserFactory.create(is_staff=True)
        # Run & check
        self.assertEqual(list(get_managed_organisations(user_1)), [org_1, org_2, ])
        self.assertEqual(list(get_managed_organisations(user_2)), [org_1, org_2, ])

    def test_can_return_only_organisations_that_are_associated_with_a_valid_subscription(self):
        # Setup
        org_1 = OrganisationFactory.create()
        org_2 = OrganisationFactory.create()
        org_3 = OrganisationFactory.create()
        user = UserFactory.create()
        org_1.members.add(user)
        org_2.members.add(user)
        org_3.members.add(user)
        subscription_1 = JournalAccessSubscriptionFactory.create(organisation=org_1)
        subscription_2 = JournalAccessSubscriptionFactory.create(organisation=org_2)
        JournalAccessSubscriptionFactory.create(organisation=org_3)
        now_dt = dt.datetime.now()
        JournalAccessSubscriptionPeriodFactory.create(
            subscription=subscription_1,
            start=now_dt - dt.timedelta(days=10),
            end=now_dt + dt.timedelta(days=8))
        JournalAccessSubscriptionPeriodFactory.create(
            subscription=subscription_2,
            start=now_dt - dt.timedelta(days=10),
            end=now_dt - dt.timedelta(days=8))
        # Run & check
        self.assertEqual(list(get_managed_organisations(user)), [org_1, ])

    def test_can_return_only_organisations_that_have_the_considered_users_in_their_members(self):
        # Setup
        org_1 = OrganisationFactory.create()
        org_2 = OrganisationFactory.create()
        org_3 = OrganisationFactory.create()
        user = UserFactory.create()
        org_1.members.add(user)
        subscription_1 = JournalAccessSubscriptionFactory.create(organisation=org_1)
        subscription_2 = JournalAccessSubscriptionFactory.create(organisation=org_2)
        subscription_3 = JournalAccessSubscriptionFactory.create(organisation=org_3)
        now_dt = dt.datetime.now()
        JournalAccessSubscriptionPeriodFactory.create(
            subscription=subscription_1,
            start=now_dt - dt.timedelta(days=10),
            end=now_dt + dt.timedelta(days=8))
        JournalAccessSubscriptionPeriodFactory.create(
            subscription=subscription_2,
            start=now_dt - dt.timedelta(days=10),
            end=now_dt + dt.timedelta(days=8))
        JournalAccessSubscriptionPeriodFactory.create(
            subscription=subscription_3,
            start=now_dt - dt.timedelta(days=10),
            end=now_dt + dt.timedelta(days=8))
        # Run & check
        self.assertEqual(list(get_managed_organisations(user)), [org_1, ])
