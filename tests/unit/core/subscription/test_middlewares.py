# -*- coding: utf-8 -*-

import datetime as dt

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory

from erudit.test import BaseEruditTestCase
from erudit.test.factories import OrganisationFactory


from base.test.factories import UserFactory
from core.subscription.middleware import SubscriptionMiddleware
from core.subscription.test.factories import InstitutionIPAddressRangeFactory
from core.subscription.test.factories import JournalAccessSubscriptionFactory
from core.subscription.test.factories import JournalAccessSubscriptionPeriodFactory


class TestSubscriptionMiddleware(BaseEruditTestCase):
    def setUp(self):
        super(TestSubscriptionMiddleware, self).setUp()
        self.factory = RequestFactory()

    def test_associates_the_subscription_type_to_the_request_in_case_of_institution(self):
        # Setup
        now_dt = dt.datetime.now()
        organisation = OrganisationFactory.create()
        subscription = JournalAccessSubscriptionFactory(
            organisation=organisation)
        JournalAccessSubscriptionPeriodFactory.create(
            subscription=subscription,
            start=now_dt - dt.timedelta(days=10),
            end=now_dt + dt.timedelta(days=8))
        InstitutionIPAddressRangeFactory.create(
            subscription=subscription,
            ip_start='192.168.1.2', ip_end='192.168.1.4')

        request = self.factory.get('/')
        request.user = AnonymousUser()
        parameters = request.META.copy()
        parameters['HTTP_X_FORWARDED_FOR'] = '192.168.1.3'
        request.META = parameters

        middleware = SubscriptionMiddleware()

        # Run
        middleware.process_request(request)

        # Check
        self.assertEqual(request.subscription_type, 'institution')
        self.assertEqual(request.subscription, subscription)

    def test_associates_the_subscription_type_to_the_request_in_case_of_individual_access(self):
        # Setup
        now_dt = dt.datetime.now()
        user = UserFactory()
        subscription = JournalAccessSubscriptionFactory.create(user=user, journal=self.journal)
        JournalAccessSubscriptionPeriodFactory.create(
            subscription=subscription,
            start=now_dt - dt.timedelta(days=10),
            end=now_dt + dt.timedelta(days=8))

        request = self.factory.get('/')
        request.user = user
        middleware = SubscriptionMiddleware()

        # Run
        middleware.process_request(request)

        # Check
        self.assertTrue(request.subscription_type == 'individual')

    def test_associates_the_subscription_type_to_the_request_in_case_of_open_access(self):
        # Setup
        request = self.factory.get('/')
        request.user = AnonymousUser()
        middleware = SubscriptionMiddleware()

        # Run
        middleware.process_request(request)

        # Check
        self.assertTrue(request.subscription_type == 'open_access')

    def test_staff_users_can_fake_ip(self):
        request = self.factory.get('/')
        request.user = UserFactory(is_staff=True)
        request.META['HTTP_X_FORWARDED_FOR'] = '1.1.1.1'
        request.META['HTTP_CLIENT_IP'] = '1.2.3.4'
        middleware = SubscriptionMiddleware()
        assert middleware._get_user_ip_address(request) == '1.2.3.4'

    def test_non_staff_users_cannot_fake_ip(self):
        request = self.factory.get('/')
        request.user = UserFactory(is_staff=False)
        request.META['HTTP_X_FORWARDED_FOR'] = '1.1.1.1'
        request.META['HTTP_CLIENT_IP'] = '1.2.3.4'
        middleware = SubscriptionMiddleware()
        assert middleware._get_user_ip_address(request) == '1.1.1.1'

    def test_anonymous_users_cannot_fake_ip(self):
        request = self.factory.get('/')
        request.user = AnonymousUser()
        request.META['HTTP_X_FORWARDED_FOR'] = '1.1.1.1'
        request.META['HTTP_CLIENT_IP'] = '1.2.3.4'
        middleware = SubscriptionMiddleware()
        assert middleware._get_user_ip_address(request) == '1.1.1.1'
