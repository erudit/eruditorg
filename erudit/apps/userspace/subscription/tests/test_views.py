from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from core.subscription.factories import PolicyFactory, IndividualAccountProfileFactory
from core.subscription.models import IndividualAccountProfile


class LoginTestCase(TestCase):

    def test_login_ok(self):
        account = IndividualAccountProfileFactory()
        account.password = '123qwe'
        account.save()
        status = self.client.login(username=account.user.username,
                                   password='123qwe')
        self.assertTrue(status)

    def test_login_ko(self):
        account = IndividualAccountProfileFactory()
        account.password = '123qwe'
        account.save()
        status = self.client.login(username=account.user.username,
                                   password='111')
        self.assertFalse(status)


class AccountListViewTestCase(TestCase):

    def setUp(self):
        self.url = reverse('userspace:subscription:account_list')

    def test_user(self):
        user = User.objects.create_user(username='user', password='user')
        self.client.login(username=user.username, password='user')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302, response.url)

    def test_staff(self):
        policy = PolicyFactory()
        user = User.objects.create_user(username='staff', password='staff')
        user.is_staff = True
        user.save()
        self.client.login(username=user.username, password='staff')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(policy))

    def test_valid_manager(self):
        policy = PolicyFactory()
        user = User.objects.create_user(username='manager', password='manager')
        self.client.login(username=user.username, password='manager')
        policy.managers.add(user)
        policy.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(policy))

    def test_anonymous(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302, response.url)

    def test_filtered_listing(self):
        policy = PolicyFactory()
        user = User.objects.create_user(username='manager', password='manager')
        policy.managers.add(user)
        policy.save()
        IndividualAccountProfileFactory.create_batch(2, policy=policy)
        IndividualAccountProfileFactory.create_batch(3)
        self.client.login(username=user.username, password='manager')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['object_list']), 2)


class AccountCreateViewTestCase(TestCase):

    def setUp(self):
        self.url = reverse('userspace:subscription:account_add')

    def test_filtered_organization(self):
        policy = PolicyFactory()
        policy2 = PolicyFactory()
        user = User.objects.create_user(username='manager', password='manager')
        self.client.login(username=user.username, password='manager')
        policy.managers.add(user)
        policy.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(policy))
        self.assertNotContains(response, str(policy2))


class AccountDeleteViewTestCase(TestCase):

    def test_permissions_ok(self):
        policy = PolicyFactory()
        user = User.objects.create_user(username='manager', password='manager')
        self.client.login(username=user.username, password='manager')
        policy.managers.add(user)
        policy.save()

        account = IndividualAccountProfileFactory(policy=policy)
        url = reverse('userspace:subscription:account_delete',
                      args=(account.pk, ))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_permissions_ko(self):
        policy = PolicyFactory()
        user = User.objects.create_user(username='manager', password='manager')
        self.client.login(username=user.username, password='manager')
        policy.managers.add(user)
        policy.save()

        account = IndividualAccountProfileFactory()
        url = reverse('userspace:subscription:account_delete',
                      args=(account.pk, ))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class AccountResetPwdViewTestCase(TestCase):

    def test_empty_pwd(self):
        policy = PolicyFactory()
        user = User.objects.create_user(username='manager', password='manager')
        self.client.login(username=user.username, password='manager')
        policy.managers.add(user)
        policy.save()

        account = IndividualAccountProfileFactory(policy=policy)
        old_pwd = account.password
        url = reverse('userspace:subscription:account_reset_pwd',
                      args=(account.pk, ))
        response = self.client.post(url, {'password': ''})
        self.assertEqual(response.status_code, 302)
        same_account = IndividualAccountProfile.objects.get(id=account.pk)
        self.assertEqual(IndividualAccountProfile.objects.count(), 1)
        self.assertNotEqual(same_account.password, old_pwd)
        self.assertEqual(same_account.user, account.user)
