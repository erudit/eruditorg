# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from faker import Factory

from core.account_actions.action_base import AccountActionBase
from core.account_actions.action_pool import actions
from core.account_actions.factories import AccountActionTokenFactory
from erudit.tests.base import BaseEruditTestCase

faker = Factory.create()

consumed = False


class TestAction(AccountActionBase):
    name = 'test-register'

    def execute(self, method):
        global consumed
        consumed = True  # noqa


class TestAccountActionRegisterView(BaseEruditTestCase):
    def tearDown(self):
        super(TestAccountActionRegisterView, self).tearDown()
        actions._registry.pop('test-register', None)
        global consumed
        consumed = False

    def test_return_an_http_403_error_if_the_user_is_already_authenticated(self):
        # Setup
        actions.register(TestAction)
        token = AccountActionTokenFactory.create(action='test-register')

        self.client.login(username='david', password='top_secret')
        url = reverse('public:account-actions:register', kwargs={'key': token.key})

        # Run
        response = self.client.get(url)

        # Check
        self.assertEqual(response.status_code, 403)

    def test_return_an_http_403_error_if_the_token_cannot_be_consumed(self):
        # Setup
        actions.register(TestAction)
        token = AccountActionTokenFactory.create(action='test-register')
        token.consume(self.user)

        self.client.logout()
        url = reverse('public:account-actions:register', kwargs={'key': token.key})

        # Run
        response = self.client.get(url)

        # Check
        self.assertEqual(response.status_code, 403)

    def test_can_properly_create_a_new_user(self):
        # Setup
        actions.register(TestAction)
        token = AccountActionTokenFactory.create(action='test-register')

        post_data = {
            'username': faker.simple_profile().get('username'),
            'email': faker.email(),
            'first_name': faker.first_name(),
            'last_name': faker.last_name(),
            'password1': 'not_secret',
            'password2': 'not_secret',
        }

        self.client.logout()
        url = reverse('public:account-actions:register', kwargs={'key': token.key})

        # Run
        response = self.client.post(url, post_data, follow=False)

        # Check
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username=post_data['username']))

    def test_can_properly_consume_a_tokenr(self):
        # Setup
        actions.register(TestAction)
        token = AccountActionTokenFactory.create(action='test-register')

        post_data = {
            'username': faker.simple_profile().get('username'),
            'email': faker.email(),
            'first_name': faker.first_name(),
            'last_name': faker.last_name(),
            'password1': 'not_secret',
            'password2': 'not_secret',
        }

        self.client.logout()
        url = reverse('public:account-actions:register', kwargs={'key': token.key})

        # Run
        response = self.client.post(url, post_data, follow=False)

        # Check
        self.assertEqual(response.status_code, 302)
        global consumed
        self.assertTrue(consumed)
