from django.test import TestCase
from django.core.urlresolvers import reverse

from individual_subscription.factories import PolicyFactory
from erudit.factories import JournalFactory
from ..factories import UserFactory


class MenuTestCase(TestCase):

    def test_menu_individual_subscription_presence(self):
        policy = PolicyFactory()
        user = UserFactory(username="user")
        user.set_password("user")
        user.save()
        policy.managers.add(user)
        policy.save()

        url = reverse('individual_subscription:account_list')
        self.client.login(username="user", password="user")
        response = self.client.get(reverse('userspace:dashboard'))
        self.assertContains(response, url)

    def test_menu_individual_subscription_absence(self):
        user = UserFactory(username="user")
        user.set_password("user")
        user.save()

        url = reverse('editor:issues')
        self.client.login(username="user", password="user")
        response = self.client.get(reverse('userspace:dashboard'))
        self.assertNotContains(response, url)

    def test_menu_issuesubscription_presence(self):
        journal = JournalFactory()
        user = UserFactory(username="user")
        user.set_password("user")
        user.save()
        journal.members.add(user)
        journal.save()

        url = reverse('editor:issues')
        self.client.login(username="user", password="user")
        response = self.client.get(reverse('userspace:dashboard'))
        self.assertContains(response, url)

    def test_menu_issuesubmission_absence(self):
        user = UserFactory(username="user")
        user.set_password("user")
        user.save()

        url = reverse('editor:issues')
        self.client.login(username="user", password="user")
        response = self.client.get(reverse('userspace:dashboard'))
        self.assertNotContains(response, url)
