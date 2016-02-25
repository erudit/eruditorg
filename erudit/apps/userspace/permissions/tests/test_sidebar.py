from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType

from core.subscription.factories import PolicyFactory
from core.permissions.models import Rule
from core.userspace.factories import UserFactory
from erudit.factories import JournalFactory


class MenuTestCase(TestCase):

    def test_menu_subscription_presence(self):
        policy = PolicyFactory()
        user = UserFactory(username="user")
        user.set_password("user")
        user.save()
        policy.managers.add(user)
        policy.save()

        url = reverse('userspace:subscription:account_list')
        self.client.login(username="user", password="user")
        response = self.client.get(reverse('userspace:dashboard'))
        self.assertContains(response, url)

    def test_menu_subscription_absence(self):
        user = UserFactory(username="user")
        user.set_password("user")
        user.save()

        url = reverse('userspace:editor:issues')
        self.client.login(username="user", password="user")
        response = self.client.get(reverse('userspace:dashboard'))
        self.assertNotContains(response, url)

    def test_menu_issuesubmission_presence(self):
        journal = JournalFactory()
        user = UserFactory(username="user")
        user.set_password("user")
        user.save()
        journal.members.add(user)
        journal.save()

        ct = ContentType.objects.get(app_label="erudit", model="journal")
        Rule.objects.create(content_type=ct,
                            user=user,
                            object_id=journal.id,
                            permission="editor.manage_issuesubmission")

        url = reverse('userspace:editor:issues')
        self.client.login(username="user", password="user")
        response = self.client.get(reverse('userspace:dashboard'))
        self.assertContains(response, url)

    def test_menu_issuesubmission_absence(self):
        user = UserFactory(username="user")
        user.set_password("user")
        user.save()

        url = reverse('userspace:editor:issues')
        self.client.login(username="user", password="user")
        response = self.client.get(reverse('userspace:dashboard'))
        self.assertNotContains(response, url)

    def test_menu_permission_presence(self):
        journal = JournalFactory()
        user = UserFactory(username="user")
        user.set_password("user")
        user.save()
        journal.members.add(user)
        journal.save()

        ct = ContentType.objects.get(app_label="erudit", model="journal")
        Rule.objects.create(content_type=ct,
                            user=user,
                            object_id=journal.id,
                            permission="userspace.manage_permissions")

        url = reverse('userspace:permissions:perm_list')
        self.client.login(username="user", password="user")
        response = self.client.get(reverse('userspace:dashboard'))
        self.assertContains(response, url)

    def test_menu_permission_absence(self):
        user = UserFactory(username="user")
        user.set_password("user")
        user.save()

        url = reverse('userspace:permissions:perm_list')
        self.client.login(username="user", password="user")
        response = self.client.get(reverse('userspace:dashboard'))
        self.assertNotContains(response, url)
