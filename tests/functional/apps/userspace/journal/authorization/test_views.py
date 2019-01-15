from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.test import TestCase

from base.test.testcases import Client
from erudit.test.factories import JournalFactory

from base.test.factories import UserFactory
from core.authorization.defaults import AuthorizationConfig as AC
from core.authorization.models import Authorization
from core.subscription.test.factories import JournalManagementPlanFactory
from core.subscription.test.factories import JournalManagementSubscriptionFactory


class TestAuthorizationUserView(TestCase):
    def setUp(self):
        super(TestAuthorizationUserView, self).setUp()
        self.user_granted = UserFactory(username="user_granted")
        self.user_non_granted = UserFactory(username="user_non_granted")

    def test_permission_list_restricted(self):
        journal = JournalFactory()
        journal.members.add(self.user_granted)
        journal.save()

        client = Client(logged_user=self.user_non_granted)
        url = reverse('userspace:journal:authorization:list', args=(journal.pk, ))

        response = client.get(url)
        self.assertEqual(response.status_code, 403)

        response = client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_permission_list_granted(self):
        journal = JournalFactory()
        journal.members.add(self.user_granted)
        journal.save()

        ct = ContentType.objects.get(app_label="erudit", model="journal")
        Authorization.objects.create(
            content_type=ct,
            user=self.user_granted,
            object_id=journal.id,
            authorization_codename=AC.can_manage_authorizations.codename)

        client = Client(logged_user=self.user_granted)
        url = reverse('userspace:journal:authorization:list', args=(journal.pk, ))
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_do_not_show_the_individual_subscription_authorization_section_without_management(self):
        # Setup
        journal = JournalFactory()
        journal.members.add(self.user_granted)
        journal.save()

        ct = ContentType.objects.get(app_label="erudit", model="journal")
        Authorization.objects.create(
            content_type=ct,
            user=self.user_granted,
            object_id=journal.id,
            authorization_codename=AC.can_manage_authorizations.codename)

        client = Client(logged_user=self.user_granted)

        url = reverse('userspace:journal:authorization:list', args=(journal.pk, ))

        # Run
        response = client.get(url, {'codename': AC.can_manage_authorizations.codename})

        # Check
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            AC.can_manage_individual_subscription.codename
            not in response.context['authorizations'])

    def test_shows_the_individual_subscription_authorization_section_with_management(self):
        # Setup
        journal = JournalFactory()
        journal.members.add(self.user_granted)
        journal.save()

        ct = ContentType.objects.get(app_label="erudit", model="journal")
        Authorization.objects.create(
            content_type=ct,
            user=self.user_granted,
            object_id=journal.id,
            authorization_codename=AC.can_manage_authorizations.codename)

        plan = JournalManagementPlanFactory.create(max_accounts=10)
        JournalManagementSubscriptionFactory.create(journal=journal, plan=plan)

        client = Client(logged_user=self.user_granted)

        url = reverse('userspace:journal:authorization:list', args=(journal.pk, ))

        # Run
        response = client.get(url, {'codename': AC.can_manage_authorizations.codename})

        # Check
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            AC.can_manage_individual_subscription.codename
            in response.context['authorizations'])


class TestAuthorizationCreateView(TestCase):
    def setUp(self):
        super(TestAuthorizationCreateView, self).setUp()
        self.user_granted = UserFactory(username="user_granted")
        self.user_non_granted = UserFactory(username="user_non_granted")

    def test_permission_create_restricted(self):
        journal = JournalFactory()
        journal.members.add(self.user_granted)
        journal.save()

        client = Client(logged_user=self.user_non_granted)
        url = reverse('userspace:journal:authorization:create', args=(journal.pk, ))

        response = client.get(url)
        self.assertEqual(response.status_code, 403)

        response = client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_permission_create_granted(self):
        journal = JournalFactory()
        journal.members.add(self.user_granted)
        journal.save()

        ct = ContentType.objects.get(app_label="erudit", model="journal")
        Authorization.objects.create(
            content_type=ct,
            user=self.user_granted,
            object_id=journal.id,
            authorization_codename=AC.can_manage_authorizations.codename)

        client = Client(logged_user=self.user_granted)
        url = reverse('userspace:journal:authorization:create', args=(journal.pk, ))
        response = client.get(url, {'codename': AC.can_manage_authorizations.codename})
        self.assertEqual(response.status_code, 200)

    def test_returns_an_http_404_error_if_the_codename_is_not_passed(self):
        # Setup
        journal = JournalFactory()
        journal.members.add(self.user_granted)
        journal.save()

        ct = ContentType.objects.get(app_label="erudit", model="journal")
        Authorization.objects.create(
            content_type=ct,
            user=self.user_granted,
            object_id=journal.id,
            authorization_codename=AC.can_manage_authorizations.codename)

        client = Client(logged_user=self.user_granted)

        url = reverse('userspace:journal:authorization:create', args=(journal.pk, ))

        # Run
        response = client.get(url)

        # Check
        self.assertEqual(response.status_code, 404)

    def test_returns_an_http_404_error_if_the_codename_is_not_known(self):
        # Setup
        journal = JournalFactory()
        journal.members.add(self.user_granted)
        journal.save()

        ct = ContentType.objects.get(app_label="erudit", model="journal")
        Authorization.objects.create(
            content_type=ct,
            user=self.user_granted,
            object_id=journal.id,
            authorization_codename=AC.can_manage_authorizations.codename)

        client = Client(logged_user=self.user_granted)

        url = reverse('userspace:journal:authorization:create', args=(journal.pk, ))

        # Run
        response = client.get(url, {'codename': 'dummy'})

        # Check
        self.assertEqual(response.status_code, 404)

    def test_can_return_an_http_403_error_if_the_journal_has_no_management_subscription(self):
        # Setup
        journal = JournalFactory()
        journal.members.add(self.user_granted)
        journal.save()

        ct = ContentType.objects.get(app_label="erudit", model="journal")
        Authorization.objects.create(
            content_type=ct,
            user=self.user_granted,
            object_id=journal.id,
            authorization_codename=AC.can_manage_authorizations.codename)

        client = Client(logged_user=self.user_granted)

        url = reverse('userspace:journal:authorization:create', args=(journal.pk, ))

        # Run
        response = client.get(
            url, {'codename': AC.can_manage_individual_subscription.codename})

        # Check
        self.assertEqual(response.status_code, 403)


class TestAuthorizationDeleteView(TestCase):
    def setUp(self):
        super(TestAuthorizationDeleteView, self).setUp()
        self.user_granted = UserFactory(username="user_granted")
        self.user_non_granted = UserFactory(username="user_non_granted")

    def test_permission_delete_restricted(self):
        client = Client(logged_user=self.user_non_granted)

        journal = JournalFactory()
        journal.save()

        client = Client(logged_user=self.user_granted)

        ct = ContentType.objects.get(app_label="erudit", model="journal")
        authorization = Authorization.objects.create(
            content_type=ct,
            user=self.user_granted,
            object_id=journal.id,
            authorization_codename=AC.can_manage_authorizations.codename)

        url = reverse('userspace:journal:authorization:delete',
                      args=(journal.pk, authorization.pk, ))

        response = client.get(url)
        self.assertEqual(response.status_code, 403)

        journal.members.add(self.user_granted)
        journal.save()
        response = client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_permission_delete_granted(self):
        journal = JournalFactory()
        journal.members.add(self.user_granted)
        journal.save()

        ct = ContentType.objects.get(app_label="erudit", model="journal")
        authorization = Authorization.objects.create(
            content_type=ct,
            user=self.user_granted,
            object_id=journal.id,
            authorization_codename=AC.can_manage_authorizations.codename)

        client = Client(logged_user=self.user_granted)
        url = reverse('userspace:journal:authorization:delete',
                      args=(journal.pk, authorization.pk, ))
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
