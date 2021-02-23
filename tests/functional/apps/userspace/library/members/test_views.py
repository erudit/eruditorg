import datetime as dt

from account_actions.models import AccountActionToken
from account_actions.test.factories import AccountActionTokenFactory
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.urls import reverse
from django.test import TestCase
from faker import Factory

from base.test.factories import UserFactory
from base.test.testcases import Client
from erudit.test.factories import OrganisationFactory

from core.authorization.defaults import AuthorizationConfig as AC
from core.authorization.test.factories import AuthorizationFactory
from core.subscription.test.factories import JournalAccessSubscriptionFactory
from core.subscription.test.factories import JournalAccessSubscriptionPeriodFactory

faker = Factory.create()


class TestOrganisationMemberListView(TestCase):
    def setUp(self):
        super(TestOrganisationMemberListView, self).setUp()
        self.user = UserFactory(is_staff=True)
        self.organisation = OrganisationFactory.create()
        self.organisation.members.add(self.user)
        self.subscription = JournalAccessSubscriptionFactory.create(organisation=self.organisation)
        now_dt = dt.datetime.now()
        JournalAccessSubscriptionPeriodFactory.create(
            subscription=self.subscription,
            start=now_dt - dt.timedelta(days=10),
            end=now_dt + dt.timedelta(days=8),
        )

    def test_cannot_be_accessed_by_a_user_who_cannot_manage_organisation_members(self):
        # Setup
        user = UserFactory()
        client = Client(logged_user=user)
        url = reverse(
            "userspace:library:members:list",
            kwargs={
                "organisation_pk": self.organisation.pk,
            },
        )

        # Run
        response = client.get(url)

        # Check
        self.assertEqual(response.status_code, 403)

    def test_provides_only_members_associated_with_the_current_organisation(self):
        # Setup
        UserFactory(username="foo", email="foo.bar@example.org", password="test_password")

        AuthorizationFactory.create(
            content_type=ContentType.objects.get_for_model(self.organisation),
            object_id=self.organisation.id,
            user=self.user,
            authorization_codename=AC.can_manage_organisation_members.codename,
        )

        client = Client(logged_user=self.user)
        url = reverse(
            "userspace:library:members:list",
            kwargs={
                "organisation_pk": self.organisation.pk,
            },
        )

        # Run
        response = client.get(url)

        # Check
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["members"]),
            [
                self.user,
            ],
        )


class TestOrganisationMemberCreateView(TestCase):
    def setUp(self):
        super(TestOrganisationMemberCreateView, self).setUp()

        self.user = UserFactory()
        self.organisation = OrganisationFactory.create()
        self.organisation.members.add(self.user)
        self.subscription = JournalAccessSubscriptionFactory.create(organisation=self.organisation)
        now_dt = dt.datetime.now()
        JournalAccessSubscriptionPeriodFactory.create(
            subscription=self.subscription,
            start=now_dt - dt.timedelta(days=10),
            end=now_dt + dt.timedelta(days=8),
        )

    def test_cannot_be_accessed_by_a_user_who_cannot_manage_organisation_members(self):
        # Setup
        user = UserFactory()
        client = Client(logged_user=user)
        url = reverse(
            "userspace:library:members:create", kwargs={"organisation_pk": self.organisation.pk}
        )

        # Run
        response = client.get(url)

        # Check
        self.assertEqual(response.status_code, 403)

    def test_can_create_an_account_action_for_the_member(self):
        # Setup
        user = UserFactory(is_staff=True)

        post_data = {
            "email": faker.email(),
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
        }

        client = Client(logged_user=user)
        url = reverse(
            "userspace:library:members:create", kwargs={"organisation_pk": self.organisation.pk}
        )

        # Run
        response = client.post(url, post_data, follow=False)

        # Check
        self.assertEqual(response.status_code, 302)
        tokens = AccountActionToken.objects.all()
        self.assertEqual(tokens.count(), 1)
        stoken = tokens.first()
        self.assertEqual(stoken.content_object, self.organisation)
        self.assertEqual(stoken.email, post_data["email"])
        self.assertEqual(stoken.first_name, post_data["first_name"])
        self.assertEqual(stoken.last_name, post_data["last_name"])

    def test_triggers_the_sending_of_a_notification_email(self):
        # Setup
        user = UserFactory(is_staff=True)

        post_data = {
            "email": faker.email(),
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
        }

        client = Client(logged_user=user)
        url = reverse(
            "userspace:library:members:create", kwargs={"organisation_pk": self.organisation.pk}
        )

        # Run
        response = client.post(url, post_data, follow=False)

        # Check
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], post_data["email"])


class TestOrganisationMemberDeleteView(TestCase):
    def setUp(self):
        super(TestOrganisationMemberDeleteView, self).setUp()
        self.user = UserFactory()
        self.organisation = OrganisationFactory.create()
        self.organisation.members.add(self.user)
        self.subscription = JournalAccessSubscriptionFactory.create(organisation=self.organisation)
        now_dt = dt.datetime.now()
        JournalAccessSubscriptionPeriodFactory.create(
            subscription=self.subscription,
            start=now_dt - dt.timedelta(days=10),
            end=now_dt + dt.timedelta(days=8),
        )

    def test_cannot_be_accessed_by_a_user_who_is_not_staff(self):
        # Setup
        user = UserFactory(username="foo", email="foo.bar@example.org", password="test_password")
        self.organisation.members.add(user)

        client = Client(logged_user=user)
        url = reverse(
            "userspace:library:members:delete",
            kwargs={
                "organisation_pk": self.organisation.pk,
                "pk": user.pk,
            },
        )

        # Run
        response = client.get(url)

        # Check
        self.assertEqual(response.status_code, 403)

    def test_can_properly_remove_a_member(self):
        # Setup
        user = UserFactory(is_staff=True)

        member = UserFactory()
        self.organisation.members.add(member)
        self.organisation.save()

        client = Client(logged_user=user)
        url = reverse(
            "userspace:library:members:delete",
            kwargs={
                "organisation_pk": self.organisation.pk,
                "pk": member.pk,
            },
        )

        # Run
        response = client.post(url, follow=False)

        # Check
        self.assertEqual(response.status_code, 302)
        self.assertEqual(list(self.organisation.members.all()), [self.user])


class TestOrganisationMemberCancelView(TestCase):
    def setUp(self):
        super(TestOrganisationMemberCancelView, self).setUp()
        self.organisation = OrganisationFactory.create()
        self.subscription = JournalAccessSubscriptionFactory.create(organisation=self.organisation)
        now_dt = dt.datetime.now()
        JournalAccessSubscriptionPeriodFactory.create(
            subscription=self.subscription,
            start=now_dt - dt.timedelta(days=10),
            end=now_dt + dt.timedelta(days=8),
        )

    def test_cannot_be_accessed_by_a_user_who_is_not_staff(self):
        # Setup
        user = UserFactory()
        token = AccountActionTokenFactory.create(content_object=self.organisation)

        client = Client(logged_user=user)
        url = reverse(
            "userspace:library:members:cancel",
            kwargs={
                "organisation_pk": self.organisation.pk,
                "pk": token.pk,
            },
        )

        # Run
        response = client.get(url)

        # Check
        self.assertEqual(response.status_code, 403)

    def test_can_cancel_an_action_token(self):
        # Setup
        user = UserFactory(is_staff=True)

        token = AccountActionTokenFactory.create(content_object=self.organisation)

        client = Client(logged_user=user)
        url = reverse(
            "userspace:library:members:cancel",
            kwargs={
                "organisation_pk": self.organisation.pk,
                "pk": token.pk,
            },
        )

        # Run
        response = client.post(url, follow=False)

        # Check
        self.assertEqual(response.status_code, 302)
        token.refresh_from_db()
        self.assertTrue(token.is_canceled)
