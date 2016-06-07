# -*- coding: utf-8 -*-

from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import User
from django.test import RequestFactory

from erudit.test import BaseEruditTestCase
from erudit.test.factories import OrganisationFactory

from ..factories import InstitutionIPAddressRangeFactory
from ..factories import JournalAccessSubscriptionFactory
from ..middleware import SubscriptionMiddleware


class TestSubscriptionMiddleware(BaseEruditTestCase):
    def setUp(self):
        super(TestSubscriptionMiddleware, self).setUp()
        self.factory = RequestFactory()

    def test_associates_the_subscription_type_to_the_request_in_case_of_institution(self):
        # Setup
        organisation = OrganisationFactory.create()
        subscription = JournalAccessSubscriptionFactory(
            organisation=organisation)
        InstitutionIPAddressRangeFactory.create(
            subscription=subscription,
            ip_start='192.168.1.2', ip_end='192.168.1.4')

        request = self.factory.get('/')
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
        user = User.objects.create_user(
            username='test', password='not_secret', email='test@exampe.com')
        JournalAccessSubscriptionFactory.create(user=user, journal=self.journal)

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
