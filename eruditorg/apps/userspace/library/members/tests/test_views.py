# -*- coding: utf-8 -*-

import datetime as dt

from account_actions.models import AccountActionToken
from account_actions.test.factories import AccountActionTokenFactory
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.core.urlresolvers import reverse
from faker import Factory

from core.authorization.defaults import AuthorizationConfig as AC
from core.authorization.factories import AuthorizationFactory
from core.subscription.factories import JournalAccessSubscriptionFactory
from core.subscription.factories import JournalAccessSubscriptionPeriodFactory
from erudit.factories import OrganisationFactory
from erudit.tests.base import BaseEruditTestCase

faker = Factory.create()


class TestOrganisationMemberListView(BaseEruditTestCase):
    def setUp(self):
        super(TestOrganisationMemberListView, self).setUp()
        self.organisation = OrganisationFactory.create()
        self.organisation.members.add(self.user)
        self.subscription = JournalAccessSubscriptionFactory.create(organisation=self.organisation)
        now_dt = dt.datetime.now()
        JournalAccessSubscriptionPeriodFactory.create(
            subscription=self.subscription,
            start=now_dt - dt.timedelta(days=10),
            end=now_dt + dt.timedelta(days=8))

    def test_cannot_be_accessed_by_a_user_who_cannot_manage_organisation_members(self):
        # Setup
        self.client.login(username='david', password='top_secret')
        url = reverse('userspace:library:members:list', kwargs={
            'organisation_pk': self.organisation.pk, })

        # Run
        response = self.client.get(url)

        # Check
        self.assertEqual(response.status_code, 403)

    def test_provides_only_members_associated_with_the_current_organisation(self):
        # Setup
        User.objects.create_user(
            username='foo', email='foo.bar@example.org', password='test_password')

        AuthorizationFactory.create(
            content_type=ContentType.objects.get_for_model(self.organisation),
            object_id=self.organisation.id, user=self.user,
            authorization_codename=AC.can_manage_organisation_members.codename)

        self.client.login(username='david', password='top_secret')
        url = reverse('userspace:library:members:list', kwargs={
            'organisation_pk': self.organisation.pk, })

        # Run
        response = self.client.get(url)

        # Check
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['members']), [self.user, ])


class TestOrganisationMemberCreateView(BaseEruditTestCase):
    def setUp(self):
        super(TestOrganisationMemberCreateView, self).setUp()
        self.organisation = OrganisationFactory.create()
        self.organisation.members.add(self.user)
        self.subscription = JournalAccessSubscriptionFactory.create(organisation=self.organisation)
        now_dt = dt.datetime.now()
        JournalAccessSubscriptionPeriodFactory.create(
            subscription=self.subscription,
            start=now_dt - dt.timedelta(days=10),
            end=now_dt + dt.timedelta(days=8))

    def test_cannot_be_accessed_by_a_user_who_cannot_manage_organisation_members(self):
        # Setup
        self.client.login(username='david', password='top_secret')
        url = reverse('userspace:library:members:create', kwargs={
            'organisation_pk': self.organisation.pk})

        # Run
        response = self.client.get(url)

        # Check
        self.assertEqual(response.status_code, 403)

    def test_can_create_an_account_action_for_the_member(self):
        # Setup
        AuthorizationFactory.create(
            content_type=ContentType.objects.get_for_model(self.organisation),
            object_id=self.organisation.id, user=self.user,
            authorization_codename=AC.can_manage_organisation_members.codename)

        post_data = {
            'email': faker.email(),
            'first_name': faker.first_name(),
            'last_name': faker.last_name(),
        }

        self.client.login(username='david', password='top_secret')
        url = reverse('userspace:library:members:create', kwargs={
            'organisation_pk': self.organisation.pk})

        # Run
        response = self.client.post(url, post_data, follow=False)

        # Check
        self.assertEqual(response.status_code, 302)
        tokens = AccountActionToken.objects.all()
        self.assertEqual(tokens.count(), 1)
        stoken = tokens.first()
        self.assertEqual(stoken.content_object, self.organisation)
        self.assertEqual(stoken.email, post_data['email'])
        self.assertEqual(stoken.first_name, post_data['first_name'])
        self.assertEqual(stoken.last_name, post_data['last_name'])

    def test_triggers_the_sending_of_a_notification_email(self):
        # Setup
        AuthorizationFactory.create(
            content_type=ContentType.objects.get_for_model(self.organisation),
            object_id=self.organisation.id, user=self.user,
            authorization_codename=AC.can_manage_organisation_members.codename)

        post_data = {
            'email': faker.email(),
            'first_name': faker.first_name(),
            'last_name': faker.last_name(),
        }

        self.client.login(username='david', password='top_secret')
        url = reverse('userspace:library:members:create', kwargs={
            'organisation_pk': self.organisation.pk})

        # Run
        response = self.client.post(url, post_data, follow=False)

        # Check
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], post_data['email'])


class TestOrganisationMemberDeleteView(BaseEruditTestCase):
    def setUp(self):
        super(TestOrganisationMemberDeleteView, self).setUp()
        self.organisation = OrganisationFactory.create()
        self.organisation.members.add(self.user)
        self.subscription = JournalAccessSubscriptionFactory.create(organisation=self.organisation)
        now_dt = dt.datetime.now()
        JournalAccessSubscriptionPeriodFactory.create(
            subscription=self.subscription,
            start=now_dt - dt.timedelta(days=10),
            end=now_dt + dt.timedelta(days=8))

    def test_cannot_be_accessed_by_a_user_who_cannot_manage_organisation_members(self):
        # Setup
        user = User.objects.create_user(
            username='foo', email='foo.bar@example.org', password='test_password')
        self.organisation.members.add(user)

        self.client.login(username='david', password='top_secret')
        url = reverse('userspace:library:members:delete', kwargs={
            'organisation_pk': self.organisation.pk, 'pk': user.pk, })

        # Run
        response = self.client.get(url)

        # Check
        self.assertEqual(response.status_code, 403)

    def test_can_properly_remove_a_member(self):
        # Setup
        user = User.objects.create_user(
            username='foo', email='foo.bar@example.org', password='test_password')
        self.organisation.members.add(user)

        AuthorizationFactory.create(
            content_type=ContentType.objects.get_for_model(self.organisation),
            object_id=self.organisation.id, user=self.user,
            authorization_codename=AC.can_manage_organisation_members.codename)

        self.client.login(username='david', password='top_secret')
        url = reverse('userspace:library:members:delete', kwargs={
            'organisation_pk': self.organisation.pk, 'pk': user.pk, })

        # Run
        response = self.client.post(url, follow=False)

        # Check
        self.assertEqual(response.status_code, 302)
        self.assertEqual(list(self.organisation.members.all()), [self.user, ])


class TestOrganisationMemberCancelView(BaseEruditTestCase):
    def setUp(self):
        super(TestOrganisationMemberCancelView, self).setUp()
        self.organisation = OrganisationFactory.create()
        self.organisation.members.add(self.user)
        self.subscription = JournalAccessSubscriptionFactory.create(organisation=self.organisation)
        now_dt = dt.datetime.now()
        JournalAccessSubscriptionPeriodFactory.create(
            subscription=self.subscription,
            start=now_dt - dt.timedelta(days=10),
            end=now_dt + dt.timedelta(days=8))

    def test_cannot_be_accessed_by_a_user_who_cannot_manage_organisation_members(self):
        # Setup
        token = AccountActionTokenFactory.create(content_object=self.organisation)

        self.client.login(username='david', password='top_secret')
        url = reverse('userspace:library:members:cancel', kwargs={
            'organisation_pk': self.organisation.pk, 'pk': token.pk, })

        # Run
        response = self.client.get(url)

        # Check
        self.assertEqual(response.status_code, 403)

    def test_can_cancel_an_action_token(self):
        # Setup
        AuthorizationFactory.create(
            content_type=ContentType.objects.get_for_model(self.organisation),
            object_id=self.organisation.id, user=self.user,
            authorization_codename=AC.can_manage_organisation_members.codename)

        token = AccountActionTokenFactory.create(content_object=self.organisation)

        self.client.login(username='david', password='top_secret')
        url = reverse('userspace:library:members:cancel', kwargs={
            'organisation_pk': self.organisation.pk, 'pk': token.pk, })

        # Run
        response = self.client.post(url, follow=False)

        # Check
        self.assertEqual(response.status_code, 302)
        token.refresh_from_db()
        self.assertFalse(token.active)
