from django.test import TestCase
from django.core.urlresolvers import reverse

from individual_subscription.factories import PolicyFactory

from .factories import UserFactory


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

        url = reverse('individual_subscription:account_list')
        self.client.login(username="user", password="user")
        response = self.client.get(reverse('userspace:dashboard'))
        self.assertNotContains(response, url)
