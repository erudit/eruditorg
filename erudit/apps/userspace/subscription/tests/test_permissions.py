
from django.test import TestCase
from django.core.urlresolvers import reverse

from base.factories import UserFactory
from core.subscription.factories import PolicyFactory, IndividualAccountFactory


class ViewsTestCase(TestCase):

    def setUp(self):
        self.user_granted = UserFactory(username="user_granted")
        self.user_granted.set_password("user")
        self.user_granted.save()

        self.user_non_granted = UserFactory(username="user_non_granted")
        self.user_non_granted.set_password("user")
        self.user_non_granted.save()

    def test_acccount_list_restricted(self):
        self.client.login(username=self.user_non_granted.username,
                          password="user")
        url = reverse('userspace:subscription:account_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_acccount_list_granted(self):
        policy = PolicyFactory()
        policy.managers.add(self.user_granted)
        policy.save()

        self.client.login(username=self.user_granted.username,
                          password="user")
        url = reverse('userspace:subscription:account_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_acccount_add_restricted(self):
        self.client.login(username=self.user_non_granted.username,
                          password="user")
        url = reverse('userspace:subscription:account_add')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_acccount_add_granted(self):
        policy = PolicyFactory()
        policy.managers.add(self.user_granted)
        policy.save()

        self.client.login(username=self.user_granted.username,
                          password="user")
        url = reverse('userspace:subscription:account_add')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_acccount_update_restricted(self):
        policy = PolicyFactory()
        account = IndividualAccountFactory(policy=policy)
        self.client.login(username=self.user_non_granted.username,
                          password="user")
        url = reverse('userspace:subscription:account_update',
                      args=(account.pk, ))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_acccount_update_granted(self):
        policy = PolicyFactory()
        policy.managers.add(self.user_granted)
        policy.save()
        account = IndividualAccountFactory(policy=policy)

        self.client.login(username=self.user_granted.username,
                          password="user")
        url = reverse('userspace:subscription:account_update',
                      args=(account.pk, ))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_acccount_delete_restricted(self):
        policy = PolicyFactory()
        policy.save()
        account = IndividualAccountFactory(policy=policy)

        self.client.login(username=self.user_non_granted.username,
                          password="user")
        url = reverse('userspace:subscription:account_delete',
                      args=(account.pk, ))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_acccount_delete_granted(self):
        policy = PolicyFactory()
        policy.managers.add(self.user_granted)
        policy.save()
        account = IndividualAccountFactory(policy=policy)

        self.client.login(username=self.user_granted.username,
                          password="user")
        url = reverse('userspace:subscription:account_delete',
                      args=(account.pk, ))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_acccount_reset_password_restricted(self):
        policy = PolicyFactory()
        policy.save()
        account = IndividualAccountFactory(policy=policy)

        self.client.login(username=self.user_non_granted.username,
                          password="user")
        url = reverse('userspace:subscription:account_reset_pwd',
                      args=(account.pk, ))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_acccount_reset_password_granted(self):
        policy = PolicyFactory()
        policy.managers.add(self.user_granted)
        policy.save()
        account = IndividualAccountFactory(policy=policy)

        self.client.login(username=self.user_granted.username,
                          password="user")
        url = reverse('userspace:subscription:account_reset_pwd',
                      args=(account.pk, ))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class RulesTestCase(TestCase):

    def test_user_cant_manage(self):
        policy = PolicyFactory()
        user = UserFactory()

        is_granted = user.has_perm('subscription.manage_policy', policy)
        self.assertEqual(is_granted, False)

    def test_user_can_manage(self):
        policy = PolicyFactory()
        user = UserFactory()
        policy.managers.add(user)
        policy.save()

        is_granted = user.has_perm('subscription.manage_policy', policy)
        self.assertEqual(is_granted, True)

    def test_superuser_can_manage(self):
        policy = PolicyFactory()
        user = UserFactory(is_superuser=True)

        is_granted = user.has_perm('subscription.manage_policy', policy)
        self.assertEqual(is_granted, True)

    def test_staff_can_manage(self):
        policy = PolicyFactory()
        user = UserFactory(is_staff=True)

        is_granted = user.has_perm('subscription.manage_policy', policy)
        self.assertEqual(is_granted, True)
