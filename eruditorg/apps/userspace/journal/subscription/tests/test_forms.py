# -*- coding: utf-8 -*-

from account_actions.models import AccountActionToken
from account_actions.test.factories import AccountActionTokenFactory
from faker import Factory

from core.subscription.account_actions import IndividualSubscriptionAction
from core.subscription.factories import JournalAccessSubscriptionFactory
from erudit.test import BaseEruditTestCase

from ..forms import JournalAccessSubscriptionCreateForm

faker = Factory.create()


class TestJournalAccessSubscriptionCreateForm(BaseEruditTestCase):
    def test_can_validate_a_basic_subscription(self):
        # Setup
        form_data = {
            'email': faker.email(),
            'first_name': faker.first_name(),
            'last_name': faker.last_name(),
        }
        form = JournalAccessSubscriptionCreateForm(form_data, journal=self.journal)
        # Run & check
        self.assertTrue(form.is_valid())

    def test_cannot_validate_if_the_email_is_already_used_by_another_subscription_token(self):
        # Setup
        AccountActionTokenFactory.create(
            action=IndividualSubscriptionAction.name, content_object=self.journal,
            email='foo@example.com')
        form_data = {
            'email': 'foo@example.com',
            'first_name': faker.first_name(),
            'last_name': faker.last_name(),
        }
        form = JournalAccessSubscriptionCreateForm(form_data, journal=self.journal)
        # Run & check
        self.assertFalse(form.is_valid())
        self.assertTrue('email' in form.errors)

    def test_cannot_validate_if_the_email_is_already_used_by_another_subscription(self):
        # Setup
        JournalAccessSubscriptionFactory.create(user=self.user, journal=self.journal)
        form_data = {
            'email': self.user.email,
            'first_name': faker.first_name(),
            'last_name': faker.last_name(),
        }
        form = JournalAccessSubscriptionCreateForm(form_data, journal=self.journal)
        # Run & check
        self.assertFalse(form.is_valid())
        self.assertTrue('email' in form.errors)

    def test_can_properly_create_a_subscription_token(self):
        # Setup
        form_data = {
            'email': faker.email(),
            'first_name': faker.first_name(),
            'last_name': faker.last_name(),
        }
        form = JournalAccessSubscriptionCreateForm(form_data, journal=self.journal)
        # Run & check
        self.assertTrue(form.is_valid())
        form.save()
        token = AccountActionToken.objects.first()
        self.assertEqual(token.email, form_data['email'])
        self.assertEqual(token.first_name, form_data['first_name'])
        self.assertEqual(token.last_name, form_data['last_name'])
        self.assertEqual(token.action, IndividualSubscriptionAction.name)
        self.assertTrue(token.can_be_consumed)
