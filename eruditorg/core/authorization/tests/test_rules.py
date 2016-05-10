# -*- coding: utf-8 -*

from django.contrib.contenttypes.models import ContentType

from base.factories import UserFactory
from core.authorization.defaults import AuthorizationConfig as AC
from core.authorization.models import Authorization
from erudit.factories import JournalFactory
from erudit.tests.base import BaseEruditTestCase


class TestManageAuthorizationRule(BaseEruditTestCase):
    def test_knows_if_a_user_cannot_manage_authorizations(self):
        user = UserFactory()
        journal = JournalFactory(collection=self.collection)
        is_granted = user.has_perm('authorization.manage_authorizations', journal)
        self.assertEqual(is_granted, False)

        journal.members.add(user)
        journal.save()
        is_granted = user.has_perm('authorization.manage_authorizations', journal)
        self.assertEqual(is_granted, False)

    def test_knows_if_a_user_can_manage_authorizations(self):
        user = UserFactory()
        journal = JournalFactory(collection=self.collection)
        journal.members.add(user)
        journal.save()
        ct = ContentType.objects.get(app_label="erudit", model="journal")
        Authorization.objects.create(
            content_type=ct,
            user=user,
            object_id=journal.id,
            authorization_codename=AC.can_manage_authorizations.codename)
        is_granted = user.has_perm('authorization.manage_authorizations', journal)
        self.assertEqual(is_granted, True)

    def test_knows_that_a_superuser_can_manage_authorizations(self):
        user = UserFactory(is_superuser=True)
        journal = JournalFactory(collection=self.collection)
        is_granted = user.has_perm('authorization.manage_authorizations', journal)
        self.assertEqual(is_granted, True)

    def test_knows_that_a_staff_member_can_manage_authorizations(self):
        user = UserFactory(is_staff=True)
        journal = JournalFactory(collection=self.collection)
        is_granted = user.has_perm('authorization.manage_authorizations', journal)
        self.assertEqual(is_granted, True)
