# -*- coding: utf-8 -*-

from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase

from ..action_base import AccountActionBase
from ..action_pool import actions
from ..exceptions import ActionAlreadyRegistered


class SimpleAction(AccountActionBase):
    name = 'simpleaction'

    def execute(self, method):
        pass


class TestAccountActionPool(TestCase):
    def tearDown(self):
        super(TestAccountActionPool, self).tearDown()
        actions.unregister_all()

    def test_can_register_simple_actions(self):
        # Setup
        actions_count_before = len(actions.get_actions())
        # Run
        actions.register(SimpleAction)
        # Check
        self.assertEqual(len(actions.get_actions()), actions_count_before + 1)
        self.assertIn(SimpleAction.name, actions._registry)
        self.assertTrue(isinstance(actions._registry[SimpleAction.name], SimpleAction))

    def test_should_raise_if_an_action_is_registered_twice(self):
        # Setup
        actions_count_before = len(actions.get_actions())
        actions.register(SimpleAction)
        # Run & check
        with self.assertRaises(ActionAlreadyRegistered):
            actions.register(SimpleAction)
        actions.unregister_all()
        actions_count_after = len(actions.get_actions())
        self.assertEqual(actions_count_before, actions_count_after)

    def test_cannot_register_a_class_which_is_not_an_action(self):
        # Setup
        actions_count_before = len(actions.get_actions())
        # Run & check
        with self.assertRaises(ImproperlyConfigured):
            actions.register(type('BadClass'))
        self.assertEqual(len(actions.get_actions()), actions_count_before)

    def test_cannot_register_erroneous_actions(self):
        # Setup
        actions_count_before = len(actions.get_actions())
        # Run & check
        with self.assertRaises(ImproperlyConfigured):
            class ErrnoneousAction1(AccountActionBase):
                pass
        with self.assertRaises(ImproperlyConfigured):
            class ErrnoneousAction2(AccountActionBase):
                name = 'test'
        actions_count_after = len(actions.get_actions())
        self.assertEqual(actions_count_before, actions_count_after)
