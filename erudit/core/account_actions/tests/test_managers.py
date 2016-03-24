# -*- coding: utf-8 -*-

import datetime as dt

from django.test import TestCase
from django.utils import timezone

from ..factories import AccountActionTokenFactory
from ..models import AccountActionToken


class TestPendingManager(TestCase):
    def test_can_return_the_pending_account_actions(self):
        # Setup
        token_1 = AccountActionTokenFactory.create()
        token_2 = AccountActionTokenFactory.create()
        token_2._meta.get_field_by_name('created')[0].auto_now_add = False
        token_2.created = timezone.now() - dt.timedelta(days=100)
        token_2.save()
        token_2._meta.get_field_by_name('created')[0].auto_now_add = True
        # Run
        tokens = AccountActionToken.pending_objects.all()
        # Check
        self.assertEqual(list(tokens), [token_1, ])
