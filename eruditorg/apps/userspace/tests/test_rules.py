# -*- coding: utf-8 -*

from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from core.authorization.defaults import AuthorizationConfig as AC
from core.authorization.factories import AuthorizationFactory
from erudit.test import BaseEruditTestCase


class TestUserspaceAccessRule(BaseEruditTestCase):
    def test_knows_that_an_anonymous_user_cannot_access_the_userspace(self):
        # Run & check
        self.assertFalse(AnonymousUser().has_perm('userspace.access'))

    def test_knows_that_a_superuser_can_access_the_userspace(self):
        # Setup
        user = User.objects.create_superuser(
            username='admin', email='admin@xyz.com', password='top_secret')
        # Run & check
        self.assertTrue(user.has_perm('userspace.access'))

    def test_knows_that_a_staff_user_can_access_the_userspace(self):
        # Setup
        user = User.objects.create_user(
            username='dummy', email='dummy@xyz.com', password='top_secret')
        user.is_staff = True
        user.save()
        # Run & check
        self.assertTrue(user.has_perm('userspace.access'))

    def test_knows_that_a_user_without_authorization_cannot_access_the_userspace(self):
        # Setup
        user = User.objects.create_user(
            username='dummy', email='dummy@xyz.com', password='top_secret')
        # Run & check
        self.assertFalse(user.has_perm('userspace.access'))

    def test_knows_that_a_user_with_the_authorization_management_authorization_can_access_the_userspace(self):  # noqa
        # Setup
        user = User.objects.create_user(
            username='dummy', email='dummy@xyz.com', password='top_secret')
        self.journal.members.add(user)
        AuthorizationFactory.create(
            content_type=ContentType.objects.get_for_model(self.journal),
            object_id=self.journal.id,
            user=user,
            authorization_codename=AC.can_manage_authorizations.codename)
        # Run & check
        self.assertTrue(user.has_perm('userspace.access'))

    def test_knows_that_a_user_with_the_issuesubmission_management_authorization_can_access_the_userspace(self):  # noqa
        # Setup
        user = User.objects.create_user(
            username='dummy', email='dummy@xyz.com', password='top_secret')
        self.journal.members.add(user)
        AuthorizationFactory.create(
            content_type=ContentType.objects.get_for_model(self.journal),
            object_id=self.journal.id,
            user=user,
            authorization_codename=AC.can_manage_issuesubmission.codename)
        # Run & check
        self.assertTrue(user.has_perm('userspace.access'))

    def test_knows_that_a_user_with_the_individual_subscription_management_authorization_can_access_the_userspace(self):  # noqa
        # Setup
        user = User.objects.create_user(
            username='dummy', email='dummy@xyz.com', password='top_secret')
        self.journal.members.add(user)
        AuthorizationFactory.create(
            content_type=ContentType.objects.get_for_model(self.journal),
            object_id=self.journal.id,
            user=user,
            authorization_codename=AC.can_manage_individual_subscription.codename)
        # Run & check
        self.assertTrue(user.has_perm('userspace.access'))

    def test_knows_that_a_user_with_the_journal_information_edit_authorization_can_access_the_userspace(self):  # noqa
        # Setup
        user = User.objects.create_user(
            username='dummy', email='dummy@xyz.com', password='top_secret')
        self.journal.members.add(user)
        AuthorizationFactory.create(
            content_type=ContentType.objects.get_for_model(self.journal),
            object_id=self.journal.id,
            user=user,
            authorization_codename=AC.can_edit_journal_information.codename)
        # Run & check
        self.assertTrue(user.has_perm('userspace.access'))
