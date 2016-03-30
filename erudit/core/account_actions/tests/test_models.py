# -*- coding: utf-8 -*-

import datetime as dt

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from ..action_base import AccountActionBase
from ..action_pool import actions
from ..conf import settings as account_actions_settings
from ..factories import AccountActionTokenFactory


test_signal = 0


class TestSignalAction(AccountActionBase):
    name = 'test-signal-action'

    def execute(self, method):
        global test_signal
        test_signal += 1  # noqa


class TestAccountActionToken(TestCase):
    def tearDown(self):
        super(TestAccountActionToken, self).tearDown()
        actions.unregister_all()

    def test_can_return_its_expiration_date(self):
        # Setup
        token = AccountActionTokenFactory.create()
        # Run & check
        self.assertEqual(
            token.expiration_date,
            token.created + dt.timedelta(
                days=account_actions_settings.ACTION_TOKEN_VALIDITY_DURATION))

    def test_can_indicate_if_it_is_expired(self):
        # Setup
        token_1 = AccountActionTokenFactory.create()
        token_2 = AccountActionTokenFactory.create()
        token_2._meta.get_field_by_name('created')[0].auto_now_add = False
        token_2.created = timezone.now() - dt.timedelta(days=100)
        token_2.save()
        token_2._meta.get_field_by_name('created')[0].auto_now_add = True
        # Run & check
        self.assertFalse(token_1.is_expired)
        self.assertTrue(token_2.is_expired)

    def test_can_indicate_if_it_is_consumed(self):
        # Setup
        user = User.objects.create_user(
            username='test', password='not_secret', email='test@exampe.com')
        token_1 = AccountActionTokenFactory.create()
        token_2 = AccountActionTokenFactory.create(user=user, consumption_date=timezone.now())
        # Run & check
        self.assertFalse(token_1.is_consumed)
        self.assertTrue(token_2.is_consumed)

    def test_can_be_consumed(self):
        # Setup
        user = User.objects.create_user(
            username='test', password='not_secret', email='test@exampe.com')
        token = AccountActionTokenFactory.create()
        # Run & check
        token.consume(user)
        self.assertTrue(token.is_consumed)

    def test_triggers_the_appropriate_signal_on_consumption(self):
        # Setup
        user = User.objects.create_user(
            username='test', password='not_secret', email='test@exampe.com')
        token = AccountActionTokenFactory.create(action='test-signal-action')
        actions.register(TestSignalAction)
        # Run & check
        token.consume(user)
        self.assertEqual(test_signal, 1)

    def test_knows_that_a_pending_token_can_be_consumed(self):
        # Setup
        token = AccountActionTokenFactory.create()
        # Run & check
        self.assertTrue(token.can_be_consumed)

    def test_knows_that_an_expired_token_cannot_be_consumed(self):
        # Setup
        token = AccountActionTokenFactory.create()
        token._meta.get_field_by_name('created')[0].auto_now_add = False
        token.created = timezone.now() - dt.timedelta(days=100)
        token.save()
        token._meta.get_field_by_name('created')[0].auto_now_add = True
        # Run & check
        self.assertFalse(token.can_be_consumed)

    def test_knows_that_a_consumed_token_cannot_be_consumed(self):
        # Setup
        user = User.objects.create_user(
            username='test', password='not_secret', email='test@exampe.com')
        token = AccountActionTokenFactory.create()
        token.consume(user)
        # Run & check
        self.assertFalse(token.can_be_consumed)

    def test_knows_that_an_inactive_token_cannot_be_consumed(self):
        # Setup
        token = AccountActionTokenFactory.create(active=False)
        # Run & check
        self.assertFalse(token.can_be_consumed)
