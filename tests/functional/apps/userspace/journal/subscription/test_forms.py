# -*- coding: utf-8 -*-

from account_actions.models import AccountActionToken
from account_actions.test.factories import AccountActionTokenFactory
from faker import Factory

from erudit.test import BaseEruditTestCase
from core.subscription.test.factories import JournalManagementSubscriptionFactory

from core.subscription.account_actions import IndividualSubscriptionAction
from core.subscription.test.factories import JournalAccessSubscriptionFactory

from apps.userspace.journal.subscription.forms import JournalAccessSubscriptionCreateForm

faker = Factory.create()


class TestJournalAccessSubscriptionCreateForm(BaseEruditTestCase):
    def test_can_validate_a_basic_subscription(self):
        subscription = JournalManagementSubscriptionFactory()

        # Setup
        form_data = {
            'email': faker.email(),
            'first_name': faker.first_name(),
            'last_name': faker.last_name(),
        }
        form = JournalAccessSubscriptionCreateForm(form_data, subscription, management_subscription=subscription)
        # Run & check
        self.assertTrue(form.is_valid())

    def test_cannot_validate_if_the_email_is_already_used_by_another_subscription_token(self):
        # Setup
        subscription = JournalManagementSubscriptionFactory()
        AccountActionTokenFactory.create(
            action=IndividualSubscriptionAction.name, content_object=subscription,
            email='foo@example.com')
        form_data = {
            'email': 'foo@example.com',
            'first_name': faker.first_name(),
            'last_name': faker.last_name(),
        }
        form = JournalAccessSubscriptionCreateForm(form_data, management_subscription=subscription)
        # Run & check
        self.assertFalse(form.is_valid())
        self.assertTrue('email' in form.errors)

    def test_cannot_validate_if_the_email_is_already_used_by_another_subscription(self):
        # Setup
        subscription = JournalManagementSubscriptionFactory()
        JournalAccessSubscriptionFactory.create(user=self.user, journal_management_subscription=subscription)
        form_data = {
            'email': self.user.email,
            'first_name': faker.first_name(),
            'last_name': faker.last_name(),
        }
        form = JournalAccessSubscriptionCreateForm(form_data, management_subscription=subscription)
        # Run & check
        self.assertFalse(form.is_valid())
        self.assertTrue('email' in form.errors)

    def test_can_properly_create_a_subscription_token(self):
        # Setup
        subscription = JournalManagementSubscriptionFactory()
        form_data = {
            'email': faker.email(),
            'first_name': faker.first_name(),
            'last_name': faker.last_name(),
        }
        form = JournalAccessSubscriptionCreateForm(form_data, management_subscription=subscription)
        # Run & check
        self.assertTrue(form.is_valid())
        form.save()
        token = AccountActionToken.objects.first()
        self.assertEqual(token.email, form_data['email'])
        self.assertEqual(token.first_name, form_data['first_name'])
        self.assertEqual(token.last_name, form_data['last_name'])
        self.assertEqual(token.action, IndividualSubscriptionAction.name)
        self.assertTrue(token.can_be_consumed)
