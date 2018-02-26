# -*- coding: utf-8 -*-
import unittest
import datetime as dt

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from django.http import HttpResponse

from erudit.test import BaseEruditTestCase
from erudit.test.factories import OrganisationFactory

from base.test.factories import UserFactory, get_anonymous_request, get_authenticated_request
from erudit.test.factories import EmbargoedArticleFactory
from core.subscription.middleware import SubscriptionMiddleware
from core.subscription.models import UserSubscriptions
from core.subscription.test.factories import InstitutionIPAddressRangeFactory
from core.subscription.test.factories import JournalAccessSubscriptionFactory
from core.subscription.test.factories import JournalAccessSubscriptionPeriodFactory
from core.subscription.test.factories import ValidJournalAccessSubscriptionPeriodFactory
from core.subscription.test.factories import InstitutionRefererFactory


class TestSubscriptionMiddleware(BaseEruditTestCase):
    def setUp(self):
        super(TestSubscriptionMiddleware, self).setUp()
        self.factory = RequestFactory()

    def test_associates_institution_subscription_to_request(self):
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

        request = get_anonymous_request()
        parameters = request.META.copy()
        parameters['HTTP_X_FORWARDED_FOR'] = '192.168.1.3'
        request.META = parameters

        middleware = SubscriptionMiddleware()

        # Run
        middleware.process_request(request)

        # Check
        assert subscription in request.subscriptions._subscriptions

    def test_associates_the_subscription_type_to_the_request_in_case_of_individual_access(self):
        # Setup
        request = get_authenticated_request()

        subscription = JournalAccessSubscriptionFactory.create(
            user=request.user,
            journal=self.journal,
            post__valid=True
        )

        middleware = SubscriptionMiddleware()

        # Run
        middleware.process_request(request)

        # Check
        assert request.subscriptions._subscriptions == [subscription]

    def test_a_user_can_have_two_subscriptions(self):

        ip_subscription = JournalAccessSubscriptionFactory(
            post__valid=True,
            post__ip_start='1.1.1.1', post__ip_end='1.1.1.1'
        )

        referer_subscription = JournalAccessSubscriptionFactory(
            post__valid=True,
            post__referers=['http://www.umontreal.ca']
        )

        request = get_anonymous_request()
        request.META['HTTP_REFERER'] = 'http://www.umontreal.ca'
        request.META['HTTP_X_FORWARDED_FOR'] = '1.1.1.1'

        middleware = SubscriptionMiddleware()
        middleware.process_request(request)

        assert set(request.subscriptions._subscriptions) == {
            ip_subscription, referer_subscription,
        }

    def test_a_user_can_have_two_individual_subscriptions(self):
        request = get_authenticated_request()

        subscriptions = JournalAccessSubscriptionFactory.create_batch(
            2,
            post__valid=True,
            user=request.user
        )

        middleware = SubscriptionMiddleware()
        middleware.process_request(request)

        assert set(request.subscriptions._subscriptions) == set(subscriptions)

    def test_referer_cookie_has_precedence_over_referer_header(self):
        request = get_anonymous_request()
        request.META['HTTP_REFERER'] = 'http://other-referer.ca'

        middleware = SubscriptionMiddleware()
        referer = middleware._get_user_referer_for_subscription(request)
        assert referer == 'http://other-referer.ca'

        request.COOKIES['HTTP_REFERER'] = 'http://www.umontreal.ca'
        referer = middleware._get_user_referer_for_subscription(request)
        assert referer == 'http://www.umontreal.ca'


    def test_associates_the_subscription_type_to_the_request_in_case_of_referer_cookie(self):
        # Setup
        request = get_anonymous_request()
        request.COOKIES['HTTP_REFERER'] = 'http://www.umontreal.ca'

        subscription = JournalAccessSubscriptionFactory(
            post__valid=True,
            post__referers=['http://www.umontreal.ca']
        )

        middleware = SubscriptionMiddleware()
        middleware.process_request(request)

        assert request.subscriptions._subscriptions == [subscription]

        request = get_anonymous_request()
        middleware.process_request(request)

        assert request.subscriptions._subscriptions == []


    def test_associates_the_subscription_type_to_the_request_in_case_of_referer_header(self):
        # Setup
        request = get_anonymous_request()
        request.META['HTTP_REFERER'] = 'http://www.umontreal.ca'

        subscription = JournalAccessSubscriptionFactory(
            post__valid=True,
            post__referers=['http://www.umontreal.ca']
        )

        middleware = SubscriptionMiddleware()
        middleware.process_request(request)

        assert request.subscriptions._subscriptions == [subscription]

        request = get_anonymous_request()
        middleware.process_request(request)

        assert request.subscriptions._subscriptions == []

    @unittest.mock.patch('core.subscription.middleware.logger')
    def test_subscription_middleware_log_requests_in_case_of_referer(self, mock_log):
        request = self.factory.get('/revues/shortname/issue/article.html')
        request.user = AnonymousUser()
        request.session = dict()
        request.META['HTTP_REFERER'] = 'http://www.umontreal.ca'

        article = EmbargoedArticleFactory()

        JournalAccessSubscriptionFactory(
            journal=article.issue.journal,
            post__valid=True,
            post__referers=['http://www.umontreal.ca']
        )

        middleware = SubscriptionMiddleware()
        middleware.process_request(request)

        request.subscriptions.set_active_subscription_for(article=article)
        assert mock_log.info.call_count == 0
        middleware.process_response(request, HttpResponse())
        assert mock_log.info.call_count == 1

        log_args = mock_log.info.call_args[0][0]
        assert len(log_args) - (len(request.META['HTTP_REFERER']) + log_args.rindex(request.META['HTTP_REFERER'])) == 0

        request = get_anonymous_request()
        request.META['HTTP_REFERER'] = 'http://www.no-referer.ca'

        middleware.process_request(request)
        middleware.process_response(request, HttpResponse())
        assert mock_log.info.call_count == 1

    @unittest.mock.patch('core.subscription.middleware.logger')
    def test_do_not_log_requests_in_case_of_ip_address_and_referer(self, mock_log):
        article = EmbargoedArticleFactory()

        # Create a subscription that has both an ip address range and a referer
        ip_subscription = JournalAccessSubscriptionFactory(
            journal=article.issue.journal,
            post__valid=True,
            post__ip_start='1.1.1.1', post__ip_end='1.1.1.1',
            post__referers=['http://umontreal.ca']
        )

        request = get_anonymous_request()
        request.META['HTTP_X_FORWARDED_FOR'] = '1.1.1.1'

        middleware = SubscriptionMiddleware()
        middleware.process_request(request)
        assert mock_log.info.call_count == 0
        request.subscriptions.set_active_subscription_for(article=article)
        middleware.process_response(request, HttpResponse())
        assert mock_log.info.call_count == 0

    def test_associates_the_subscription_type_to_the_request_in_case_of_referer_in_session(self):
        # Setup
        request = get_anonymous_request()
        request.session = {'HTTP_REFERER': 'http://www.umontreal.ca'}
        request.META['HTTP_REFERER'] = 'http://www.erudit.org'

        article = EmbargoedArticleFactory()

        subscription = JournalAccessSubscriptionFactory(
            journal=article.issue.journal,
            post__valid=True,
            post__referers=['http://www.umontreal.ca']
        )

        middleware = SubscriptionMiddleware()
        middleware.process_request(request)

        assert request.subscriptions._subscriptions == [subscription]

    def test_associates_the_subscription_type_to_the_request_in_case_of_open_access(self):
        # Setup
        request = get_anonymous_request()

        middleware = SubscriptionMiddleware()

        # Run
        middleware.process_request(request)

        # Check
        assert request.subscriptions._subscriptions == []

    def test_staff_users_can_fake_ip(self):
        request = self.factory.get('/')
        request.user = UserFactory(is_staff=True)
        request.session = dict()
        request.META['HTTP_X_FORWARDED_FOR'] = '1.1.1.1'
        request.META['HTTP_CLIENT_IP'] = '1.2.3.4'
        middleware = SubscriptionMiddleware()
        assert middleware._get_user_ip_address(request) == '1.2.3.4'

    def test_non_staff_users_cannot_fake_ip(self):
        request = self.factory.get('/')
        request.user = UserFactory(is_staff=False)
        request.session = dict()
        request.META['HTTP_X_FORWARDED_FOR'] = '1.1.1.1'
        request.META['HTTP_CLIENT_IP'] = '1.2.3.4'
        middleware = SubscriptionMiddleware()
        assert middleware._get_user_ip_address(request) == '1.1.1.1'

    def test_anonymous_users_cannot_fake_ip(self):
        request = self.factory.get('/')
        request.user = AnonymousUser()
        request.session = dict()
        request.META['HTTP_X_FORWARDED_FOR'] = '1.1.1.1'
        request.META['HTTP_CLIENT_IP'] = '1.2.3.4'
        middleware = SubscriptionMiddleware()
        assert middleware._get_user_ip_address(request) == '1.1.1.1'
