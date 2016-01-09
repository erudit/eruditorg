from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from ..factories import OrganizationPolicyFactory, IndividualAccountFactory
from ..models import IndividualAccount


class AccountListViewTestCase(TestCase):

    def setUp(self):
        self.url = reverse('individual_subscription:account_list')

    def test_user(self):
        user = User.objects.create_user(username='user', password='user')
        self.client.login(username=user.username, password='user')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302, response.url)

    def test_staff(self):
        policy = OrganizationPolicyFactory()
        user = User.objects.create_user(username='staff', password='staff')
        user.is_staff = True
        user.save()
        self.client.login(username=user.username, password='staff')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(policy))

    def test_valid_manager(self):
        policy = OrganizationPolicyFactory()
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
        policy = OrganizationPolicyFactory()
        user = User.objects.create_user(username='manager', password='manager')
        policy.managers.add(user)
        policy.save()
        IndividualAccountFactory.create_batch(2, organization_policy=policy)
        IndividualAccountFactory.create_batch(3)
        self.client.login(username=user.username, password='manager')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['object_list']), 2)


class AccountCreateViewTestCase(TestCase):

    def setUp(self):
        self.url = reverse('individual_subscription:account_add')

    def test_filtered_organization(self):
        policy = OrganizationPolicyFactory()
        policy2 = OrganizationPolicyFactory()
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
        policy = OrganizationPolicyFactory()
        user = User.objects.create_user(username='manager', password='manager')
        self.client.login(username=user.username, password='manager')
        policy.managers.add(user)
        policy.save()

        account = IndividualAccountFactory(organization_policy=policy)
        url = reverse('individual_subscription:account_delete',
                      args=(account.pk, ))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_permissions_ko(self):
        policy = OrganizationPolicyFactory()
        user = User.objects.create_user(username='manager', password='manager')
        self.client.login(username=user.username, password='manager')
        policy.managers.add(user)
        policy.save()

        account = IndividualAccountFactory()
        url = reverse('individual_subscription:account_delete',
                      args=(account.pk, ))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class AccountResetPwdViewTestCase(TestCase):

    def test_empty_pwd(self):
        policy = OrganizationPolicyFactory()
        user = User.objects.create_user(username='manager', password='manager')
        self.client.login(username=user.username, password='manager')
        policy.managers.add(user)
        policy.save()

        account = IndividualAccountFactory(organization_policy=policy)
        old_pwd = account.password
        url = reverse('individual_subscription:account_reset_pwd',
                      args=(account.pk, ))
        response = self.client.post(url, {'password': ''})
        self.assertEqual(response.status_code, 302)
        same_account = IndividualAccount.objects.get(id=account.pk)
        self.assertEqual(IndividualAccount.objects.count(), 1)
        self.assertNotEqual(same_account.password, old_pwd)
        self.assertEqual(same_account.email, account.email)
