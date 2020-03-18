# -*- coding: utf-8 -*-

from account_actions.action_base import AccountActionBase
from account_actions.action_pool import actions
from account_actions.test.factories import AccountActionTokenFactory
from django.contrib.auth.models import User
from django.test import TestCase
from faker import Factory

from apps.public.account_actions.forms import AccountActionRegisterForm

faker = Factory.create()

consumed = False


class TestAction(AccountActionBase):
    name = 'test-consumed'

    def execute(self, method):
        global consumed
        consumed = True  # noqa


class TestAccountActionRegisterForm(TestCase):
    def tearDown(self):
        super(TestAccountActionRegisterForm, self).tearDown()
        actions._registry.pop('test-consumed', None)

    def test_can_initialize_the_email_address_using_the_token(self):
        # Setup
        token = AccountActionTokenFactory.create(email='test@example.com')
        # Run
        form = AccountActionRegisterForm(token=token)
        # Check
        self.assertEqual(form.fields['email'].initial, 'test@example.com')

    def test_can_initialize_the_first_name_using_the_token(self):
        # Setup
        token = AccountActionTokenFactory.create(first_name='foo')
        # Run
        form = AccountActionRegisterForm(token=token)
        # Check
        self.assertEqual(form.fields['first_name'].initial, 'foo')

    def test_can_initialize_the_last_name_using_the_token(self):
        # Setup
        token = AccountActionTokenFactory.create(last_name='bar')
        # Run
        form = AccountActionRegisterForm(token=token)
        # Check
        self.assertEqual(form.fields['last_name'].initial, 'bar')

    def test_cannot_be_validated_if_a_user_with_the_same_email_address_already_exists(self):
        # Setup
        User.objects.create_user(
            username='test@example.com', password='not_secret', email='test@exampe.com')
        token = AccountActionTokenFactory.create(email='test@exampe.com')
        form_data = {
            'username': faker.simple_profile().get('mail'),
            'email': 'test@exampe.com',
            'first_name': faker.first_name(),
            'last_name': faker.last_name(),
            'password1': 'not_secret',
            'password2': 'not_secret',
        }
        # Run
        form = AccountActionRegisterForm(form_data, token=token)
        # Check
        self.assertFalse(form.is_valid())
        self.assertTrue('email' in form.errors)

    def test_can_properly_create_a_user(self):
        # Setup
        token = AccountActionTokenFactory.create()
        form_data = {
            'username': faker.simple_profile().get('mail'),
            'email': faker.email(),
            'first_name': faker.first_name(),
            'last_name': faker.last_name(),
            'password1': 'not_secret',
            'password2': 'not_secret',
        }
        # Run & check
        form = AccountActionRegisterForm(form_data, token=token)
        self.assertTrue(form.is_valid())
        form.save()
        user = User.objects.first()
        self.assertEqual(user.username, form_data['email'])
        self.assertEqual(user.email, form_data['email'])
        self.assertEqual(user.first_name, form_data['first_name'])
        self.assertEqual(user.last_name, form_data['last_name'])
        self.assertTrue(user.check_password('not_secret'))

    def test_can_properly_consume_the_token(self):
        # Setup
        actions.register(TestAction)
        token = AccountActionTokenFactory.create(action='test-consumed')
        form_data = {
            'username': faker.simple_profile().get('mail'),
            'email': faker.email(),
            'first_name': faker.first_name(),
            'last_name': faker.last_name(),
            'password1': 'not_secret',
            'password2': 'not_secret',
        }
        # Run & check
        form = AccountActionRegisterForm(form_data, token=token)
        self.assertTrue(form.is_valid())
        form.save()
        global consumed
        self.assertTrue(consumed)
