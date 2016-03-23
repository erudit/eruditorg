# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.test import TestCase

from ..action_base import AccountActionBase
from ..action_pool import actions
from ..factories import AccountActionTokenFactory


email_sent = False
execute_called = False


class TestEmailNotificationAction(AccountActionBase):
    name = 'test-email-notification'

    def execute(self, method):
        pass

    def send_notification_email(self, token):
        global email_sent
        email_sent = True


class TestExecuteAction(AccountActionBase):
    name = 'test-execute'

    def execute(self, method):
        pass

    def send_notification_email(self, token):
        global execute_called
        execute_called = True


class TestSendCreationNotificationEmailReceiver(TestCase):
    def tearDown(self):
        super(TestSendCreationNotificationEmailReceiver, self).tearDown()
        actions.unregister_all()

    def test_can_send_a_notification_on_token_creation(self):
        # Setup
        actions.register(TestEmailNotificationAction)
        # Run & check
        AccountActionTokenFactory.create(action='test-email-notification')
        self.assertTrue(email_sent)


class TestExecuteActionReceiver(TestCase):
    def tearDown(self):
        super(TestExecuteActionReceiver, self).tearDown()
        actions.unregister_all()

    def test_can_execute_the_action_after_consumption(self):
        # Setup
        actions.register(TestExecuteAction)
        token = AccountActionTokenFactory.create(action='test-execute')
        user = User.objects.create_user(
            username='test', password='not_secret', email='test@exampe.com')
        # Run & check
        token.consume(user)
        self.assertTrue(execute_called)
