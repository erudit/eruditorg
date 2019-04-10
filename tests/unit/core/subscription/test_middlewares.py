import unittest
import datetime as dt

import pytest
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, override_settings
from django.http import HttpResponse

from erudit.test.factories import OrganisationFactory

from base.test.factories import UserFactory, get_anonymous_request, get_authenticated_request
from erudit.test.factories import EmbargoedArticleFactory, JournalFactory
from core.subscription.middleware import SubscriptionMiddleware
from core.subscription.test.factories import InstitutionIPAddressRangeFactory
from core.subscription.test.factories import JournalAccessSubscriptionFactory
from core.subscription.test.factories import JournalAccessSubscriptionPeriodFactory
from core.subscription.test.utils import generate_casa_token

pytestmark = pytest.mark.django_db


class TestSubscriptionMiddleware:
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
        journal = JournalFactory()
        request = get_authenticated_request()

        subscription = JournalAccessSubscriptionFactory.create(
            user=request.user,
            journals=[journal],
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
        request = RequestFactory().get('/revues/shortname/issue/article.html')
        request.user = AnonymousUser()
        request.session = dict()
        request.META['HTTP_REFERER'] = 'http://www.umontreal.ca'

        article = EmbargoedArticleFactory()

        JournalAccessSubscriptionFactory(
            journals=[article.issue.journal],
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
            journals=[article.issue.journal],
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
            journals=[article.issue.journal],
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
        request = RequestFactory().get('/')
        request.user = UserFactory(is_staff=True)
        request.session = dict()
        request.META['HTTP_X_FORWARDED_FOR'] = '1.1.1.1'
        request.META['HTTP_CLIENT_IP'] = '1.2.3.4'
        middleware = SubscriptionMiddleware()
        assert middleware._get_user_ip_address(request) == '1.2.3.4'

    def test_non_staff_users_cannot_fake_ip(self):
        request = RequestFactory().get('/')
        request.user = UserFactory(is_staff=False)
        request.session = dict()
        request.META['HTTP_X_FORWARDED_FOR'] = '1.1.1.1'
        request.META['HTTP_CLIENT_IP'] = '1.2.3.4'
        middleware = SubscriptionMiddleware()
        assert middleware._get_user_ip_address(request) == '1.1.1.1'

    def test_anonymous_users_cannot_fake_ip(self):
        request = RequestFactory().get('/')
        request.user = AnonymousUser()
        request.session = dict()
        request.META['HTTP_X_FORWARDED_FOR'] = '1.1.1.1'
        request.META['HTTP_CLIENT_IP'] = '1.2.3.4'
        middleware = SubscriptionMiddleware()
        assert middleware._get_user_ip_address(request) == '1.1.1.1'

    @pytest.mark.parametrize('kwargs, nonce_count, authorized', (
        # Valid token
        ({}, 1, True),
        # Badly formed token
        ({'token_separator': '!'}, 1, False),
        # Invalid nonce
        ({'invalid_nonce': True}, 1, False),
        # Invalid message
        ({'invalid_message': True}, 1, False),
        # Invalid signature
        ({'invalid_signature': True}, 1, False),
        # Nonce seen more than 3 times
        ({}, 4, False),
        # Badly formatted payload
        ({'payload_separator': '!'}, 1, False),
        # Expired token
        ({'time_delta': 3600000001}, 1, False),
        # Wrong IP
        ({'ip_subnet': '8.8.8.0/24'}, 1, False),
        # Invalid subscription
        ({'subscription_id': 2}, 1, False),
    ))
    @unittest.mock.patch('core.subscription.middleware.SubscriptionMiddleware._nonce_count')
    @override_settings(GOOGLE_CASA_KEY='74796E8FF6363EFF91A9308D1D05335E')
    def test_casa_authorize(self, mock_nonce_count, kwargs, nonce_count, authorized):
        mock_nonce_count.return_value = nonce_count
        subscription = JournalAccessSubscriptionFactory(pk=1, post__valid=True)
        request = RequestFactory().get('/', {
            'casa_token': generate_casa_token(**kwargs),
        }, follow=True)
        request.user = AnonymousUser()
        request.session = dict()
        middleware = SubscriptionMiddleware()
        middleware.process_request(request)
        if authorized:
            assert subscription in request.subscriptions._subscriptions
        else:
            assert subscription not in request.subscriptions._subscriptions
