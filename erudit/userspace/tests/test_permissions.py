from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType

from userspace.factories import UserFactory

from erudit.factories import JournalFactory
from permissions.models import Rule


class ViewsTestCase(TestCase):

    def setUp(self):
        self.user_granted = UserFactory(username="user_granted")
        self.user_granted.set_password("user")
        self.user_granted.save()

        self.user_non_granted = UserFactory(username="user_non_granted")
        self.user_non_granted.set_password("user")
        self.user_non_granted.save()

    def test_permission_list_restricted(self):
        self.client.login(username=self.user_non_granted.username,
                          password="user")
        url = reverse('userspace:perm_list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        journal = JournalFactory()
        journal.members.add(self.user_granted)
        journal.save()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_permission_list_granted(self):
        journal = JournalFactory()
        journal.members.add(self.user_granted)
        journal.save()

        ct = ContentType.objects.get(app_label="erudit", model="journal")
        Rule.objects.create(content_type=ct,
                            user=self.user_granted,
                            object_id=journal.id,
                            permission="userspace.manage_permissions")

        self.client.login(username=self.user_granted.username,
                          password="user")
        url = reverse('userspace:perm_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_permission_create_restricted(self):
        self.client.login(username=self.user_non_granted.username,
                          password="user")
        url = reverse('userspace:perm_create')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        journal = JournalFactory()
        journal.members.add(self.user_granted)
        journal.save()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_permission_create_granted(self):
        journal = JournalFactory()
        journal.members.add(self.user_granted)
        journal.save()

        ct = ContentType.objects.get(app_label="erudit", model="journal")
        Rule.objects.create(content_type=ct,
                            user=self.user_granted,
                            object_id=journal.id,
                            permission='userspace.manage_permissions')

        self.client.login(username=self.user_granted.username,
                          password="user")
        url = reverse('userspace:perm_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_permission_delete_restricted(self):
        self.client.login(username=self.user_non_granted.username,
                          password="user")

        journal = JournalFactory()
        journal.save()

        ct = ContentType.objects.get(app_label="erudit", model="journal")
        rule = Rule.objects.create(content_type=ct,
                                   user=self.user_granted,
                                   object_id=journal.id,
                                   permission='userspace.manage_permissions')

        url = reverse('userspace:perm_delete', args=(rule.pk, ))

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        journal.members.add(self.user_non_granted)
        journal.save()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_permission_delete_granted(self):
        journal = JournalFactory()
        journal.members.add(self.user_granted)
        journal.save()

        ct = ContentType.objects.get(app_label="erudit", model="journal")
        rule = Rule.objects.create(content_type=ct,
                                   user=self.user_granted,
                                   object_id=journal.id,
                                   permission='userspace.manage_permissions')

        self.client.login(username=self.user_granted.username,
                          password="user")
        url = reverse('userspace:perm_delete', args=(rule.pk, ))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class RulesTestCase(TestCase):

    def test_user_cant_manage(self):
        user = UserFactory()
        journal = JournalFactory()
        is_granted = user.has_perm('userspace.manage_permissions', journal)
        self.assertEqual(is_granted, False)

        journal.members.add(user)
        journal.save()
        is_granted = user.has_perm('userspace.manage_permissions', journal)
        self.assertEqual(is_granted, False)

    def test_user_can_manage(self):
        user = UserFactory()
        journal = JournalFactory()
        journal.members.add(user)
        journal.save()
        ct = ContentType.objects.get(app_label="erudit", model="journal")
        Rule.objects.create(content_type=ct,
                            user=user,
                            object_id=journal.id,
                            permission="userspace.manage_permissions")
        is_granted = user.has_perm('userspace.manage_permissions', journal)
        self.assertEqual(is_granted, True)

    def test_superuser_can_manage(self):
        user = UserFactory(is_superuser=True)
        journal = JournalFactory()
        is_granted = user.has_perm('userspace.manage_permissions', journal)
        self.assertEqual(is_granted, True)

    def test_staff_can_manage(self):
        user = UserFactory(is_staff=True)
        journal = JournalFactory()
        is_granted = user.has_perm('userspace.manage_permissions', journal)
        self.assertEqual(is_granted, True)
