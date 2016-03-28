# -*- coding: utf-8 -*-

from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import User
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import Http404
from django.test import RequestFactory
from django.test import TestCase

from ..action_base import AccountActionBase
from ..action_pool import actions
from ..factories import AccountActionTokenFactory
from ..views.generic import AccountActionLandingView
from ..views.generic import AccountActionConsumeView


class Action1(AccountActionBase):
    name = 'action-1'

    def execute(self, method):  # pragma: no cover
        pass


class Action2(AccountActionBase):
    name = 'action-2'
    landing_page_template_name = 'action-2.html'

    def execute(self, method):  # pragma: no cover
        pass


class TestAccountActionLandingView(TestCase):
    def setUp(self):
        super(TestAccountActionLandingView, self).setUp()
        self.factory = RequestFactory()

    def tearDown(self):
        super(TestAccountActionLandingView, self).tearDown()
        actions.unregister_all()

    def test_return_an_http_404_error_if_the_token_cannot_be_found(self):
        # Setup
        view = AccountActionLandingView.as_view()
        request = self.factory.get('/')
        # Run & check
        with self.assertRaises(Http404):
            view(request, key='dummy')

    def test_return_an_http_404_error_if_the_token_action_is_not_registered(self):
        # Setup
        token = AccountActionTokenFactory.create()
        view = AccountActionLandingView.as_view()
        request = self.factory.get('/')
        # Run & check
        with self.assertRaises(Http404):
            view(request, key=token.key)

    def test_embeds_the_action_configuration_into_the_context(self):
        # Setup
        actions.register(Action1)
        token = AccountActionTokenFactory.create(action='action-1')

        user = User.objects.create_user(
            username='test', password='not_secret', email='test@exampe.com')
        request = self.factory.get('/')
        request.user = user

        view = AccountActionLandingView.as_view()

        # Run
        response = view(request, key=token.key)

        # Check
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.context_data['action'], Action1))

    def test_can_use_the_template_specified_in_the_action_configuration(self):
        # Setup
        actions.register(Action2)
        token = AccountActionTokenFactory.create(action='action-2')

        user = User.objects.create_user(
            username='test', password='not_secret', email='test@exampe.com')
        request = self.factory.get('/')
        request.user = user

        view = AccountActionLandingView.as_view()

        # Run
        response = view(request, key=token.key)

        # Check
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, ['action-2.html', ])


class TestAccountActionConsumeView(TestCase):
    def setUp(self):
        super(TestAccountActionConsumeView, self).setUp()
        self.factory = RequestFactory()

    def tearDown(self):
        super(TestAccountActionConsumeView, self).tearDown()
        actions.unregister_all()

    def test_return_an_http_403_error_if_the_user_is_not_authenticated(self):
        # Setup
        actions.register(Action1)
        token = AccountActionTokenFactory.create(action='action-1')

        request = self.factory.post('/')
        request.user = AnonymousUser()

        view = AccountActionConsumeView.as_view()

        # Run & check
        with self.assertRaises(PermissionDenied):
            view(request, key=token.key)

    def test_return_an_http_403_error_if_the_action_cannot_be_consumed(self):
        # Setup
        actions.register(Action1)
        token = AccountActionTokenFactory.create(action='action-1')

        user = User.objects.create_user(
            username='test', password='not_secret', email='test@exampe.com')
        token.consume(user)

        request = self.factory.post('/')
        request.user = user

        view = AccountActionConsumeView.as_view()

        # Run & check
        with self.assertRaises(PermissionDenied):
            view(request, key=token.key)

    def test_can_consume_an_action_token(self):
        # Setup
        actions.register(Action1)
        token = AccountActionTokenFactory.create(action='action-1')

        user = User.objects.create_user(
            username='test', password='not_secret', email='test@exampe.com')

        session_middleware = SessionMiddleware()
        message_middleware = MessageMiddleware()
        request = self.factory.post('/')
        session_middleware.process_request(request)
        message_middleware.process_request(request)
        request.user = user

        view = AccountActionConsumeView.as_view()

        # Run
        response = view(request, key=token.key)

        # Check
        self.assertEqual(response.status_code, 302)
        token.refresh_from_db()
        self.assertTrue(token.is_consumed)
