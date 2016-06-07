# -*- coding: utf-8 -*-

import datetime as dt

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from erudit.test import BaseEruditTestCase
from erudit.test.factories import OrganisationFactory

from core.authorization.defaults import AuthorizationConfig as AC
from core.authorization.factories import AuthorizationFactory

from ..factories import JournalAccessSubscriptionFactory
from ..factories import JournalAccessSubscriptionPeriodFactory
from ..factories import JournalManagementPlanFactory
from ..factories import JournalManagementSubscriptionFactory


class TestManageIndividualSubscriptionRule(BaseEruditTestCase):
    def test_knows_that_a_superuser_can_manage_individual_subscriptions(self):
        # Setup
        user = User.objects.create_superuser(
            username='admin', email='admin@xyz.com', password='top_secret')
        # Run & check
        self.assertTrue(user.has_perm('subscription.manage_individual_subscription', self.journal))

    def test_knows_that_a_staff_member_can_manage_individual_subscriptions(self):
        # Setup
        user = User.objects.create_user(
            username='staff', email='admin@xyz.com', password='top_secret')
        user.is_staff = True
        user.save()
        # Run & check
        self.assertTrue(user.has_perm('subscription.manage_individual_subscription', self.journal))

    def test_knows_if_a_simple_user_can_manage_individual_subscriptions(self):
        # Setup
        AuthorizationFactory.create(
            content_type=ContentType.objects.get_for_model(self.journal), object_id=self.journal.id,
            user=self.user, authorization_codename=AC.can_manage_individual_subscription.codename)
        plan = JournalManagementPlanFactory.create(max_accounts=10)
        JournalManagementSubscriptionFactory.create(journal=self.journal, plan=plan)
        # Run & check
        self.assertTrue(
            self.user.has_perm('subscription.manage_individual_subscription', self.journal))

    def test_knows_if_a_simple_user_cannot_manage_individual_subscriptions(self):
        # Setup
        user = User.objects.create_user(
            username='test', email='test@xyz.com', password='top_secret')
        # Run & check
        self.assertFalse(user.has_perm('subscription.manage_individual_subscription', self.journal))


class TestManageOrganisationSubscriptionIpsRule(BaseEruditTestCase):
    def setUp(self):
        super(TestManageOrganisationSubscriptionIpsRule, self).setUp()
        self.organisation = OrganisationFactory.create()

    def test_knows_that_a_superuser_can_manage_organisation_subscription_ips(self):
        # Setup
        user = User.objects.create_superuser(
            username='admin', email='admin@xyz.com', password='top_secret')
        # Run & check
        self.assertTrue(
            user.has_perm('subscription.manage_organisation_subscription_ips', self.organisation))

    def test_knows_that_a_staff_member_can_manage_organisation_subscription_ips(self):
        # Setup
        user = User.objects.create_user(
            username='staff', email='admin@xyz.com', password='top_secret')
        user.is_staff = True
        user.save()
        # Run & check
        self.assertTrue(
            user.has_perm('subscription.manage_organisation_subscription_ips', self.organisation))

    def test_knows_if_a_simple_user_can_manage_organisation_subscription_ips(self):
        # Setup
        AuthorizationFactory.create(
            content_type=ContentType.objects.get_for_model(self.organisation),
            object_id=self.organisation.id, user=self.user,
            authorization_codename=AC.can_manage_organisation_subscription_ips.codename)
        self.organisation.members.add(self.user)
        subscription = JournalAccessSubscriptionFactory.create(
            journal=self.journal, organisation=self.organisation)
        now_dt = dt.datetime.now()
        JournalAccessSubscriptionPeriodFactory.create(
            subscription=subscription,
            start=now_dt - dt.timedelta(days=8),
            end=now_dt + dt.timedelta(days=11))
        # Run & check
        self.assertTrue(
            self.user.has_perm(
                'subscription.manage_organisation_subscription_ips', self.organisation))

    def test_knows_if_a_simple_user_cannot_manage_organisation_subscription_ips(self):
        # Setup
        user = User.objects.create_user(
            username='test', email='test@xyz.com', password='top_secret')
        # Run & check
        self.assertFalse(
            user.has_perm('subscription.manage_organisation_subscription_ips', self.organisation))
