# -*- coding: utf-8 -*-

from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.models import ContentType

from base.factories import GroupFactory
from erudit.tests import BaseEruditTestCase

from ..defaults import AuthorizationConfig as AC
from ..factories import AuthorizationFactory
from ..predicates import HasAuthorization


class TestHasAuthorizationPredicate(BaseEruditTestCase):
    def test_can_check_if_a_user_has_an_authorization(self):
        # Setup
        AuthorizationFactory.create(
            user=self.user, authorization_codename=AC.can_manage_authorizations.codename)
        auth_check_1 = HasAuthorization(AC.can_manage_authorizations)
        auth_check_2 = HasAuthorization(AC.can_manage_individual_subscription)
        # Run & check
        self.assertTrue(auth_check_1(self.user))
        self.assertFalse(auth_check_2(self.user))

    def test_can_check_if_a_user_has_an_authorization_using_its_group(self):
        # Setup
        group = GroupFactory.create()
        self.user.groups.add(group)
        AuthorizationFactory.create(
            group=group, authorization_codename=AC.can_manage_authorizations.codename)
        auth_check_1 = HasAuthorization(AC.can_manage_authorizations)
        auth_check_2 = HasAuthorization(AC.can_manage_individual_subscription)
        # Run & check
        self.assertTrue(auth_check_1(self.user))
        self.assertFalse(auth_check_2(self.user))

    def test_can_check_if_a_user_has_an_authorization_on_a_specific_object(self):
        # Setup
        object_id = self.journal.id
        content_type = ContentType.objects.get_for_model(self.journal)
        AuthorizationFactory.create(
            user=self.user, authorization_codename=AC.can_manage_authorizations.codename,
            content_type=content_type, object_id=object_id)
        auth_check_1 = HasAuthorization(AC.can_manage_authorizations)
        auth_check_2 = HasAuthorization(AC.can_manage_individual_subscription)
        # Run & check
        self.assertTrue(auth_check_1(self.user, self.journal))
        self.assertFalse(auth_check_2(self.user, self.journal))

    def test_can_check_if_a_user_has_an_authorization_on_a_specific_object_foreign_key(self):
        # Setup
        object_id = self.journal.collection.id
        content_type = ContentType.objects.get_for_model(self.journal.collection)
        AuthorizationFactory.create(
            user=self.user, authorization_codename=AC.can_manage_authorizations.codename,
            content_type=content_type, object_id=object_id)
        auth_check_1 = HasAuthorization(AC.can_manage_authorizations, 'collection')
        auth_check_2 = HasAuthorization(AC.can_manage_individual_subscription, 'collection')
        # Run & check
        self.assertTrue(auth_check_1(self.user, self.journal))
        self.assertFalse(auth_check_2(self.user, self.journal))

    def test_knows_that_anonymous_users_cannot_have_authorizations(self):
        # Setup
        user = AnonymousUser()
        auth_check_1 = HasAuthorization(AC.can_manage_authorizations, 'collection')
        auth_check_2 = HasAuthorization(AC.can_manage_individual_subscription, 'collection')
        # Run & check
        self.assertFalse(auth_check_1(user, self.journal))
        self.assertFalse(auth_check_2(user, self.journal))
