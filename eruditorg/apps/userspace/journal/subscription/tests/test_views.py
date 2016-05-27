# -*- coding; utf-8 -*-

from account_actions.models import AccountActionToken
from account_actions.test.factories import AccountActionTokenFactory
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.core.urlresolvers import reverse
from faker import Factory

from core.authorization.defaults import AuthorizationConfig as AC
from core.authorization.factories import AuthorizationFactory
from core.subscription.factories import JournalAccessSubscriptionFactory
from core.subscription.factories import JournalManagementPlanFactory
from core.subscription.factories import JournalManagementSubscriptionFactory
from core.subscription.models import JournalAccessSubscription
from erudit.factories import JournalFactory
from erudit.tests.base import BaseEruditTestCase

faker = Factory.create()


class TestIndividualJournalAccessSubscriptionListView(BaseEruditTestCase):
    def test_cannot_be_accessed_by_a_user_who_cannot_manage_individual_subscriptions(self):
        # Setup
        self.client.login(username='david', password='top_secret')
        url = reverse('userspace:journal:subscription:list', kwargs={
            'journal_pk': self.journal.pk, })

        # Run
        response = self.client.get(url)

        # Check
        self.assertEqual(response.status_code, 403)

    def test_provides_only_subscriptions_associated_with_the_current_journal(self):
        # Setup
        AuthorizationFactory.create(
            content_type=ContentType.objects.get_for_model(self.journal), object_id=self.journal.id,
            user=self.user, authorization_codename=AC.can_manage_individual_subscription.codename)

        plan = JournalManagementPlanFactory.create(max_accounts=10)
        JournalManagementSubscriptionFactory.create(journal=self.journal, plan=plan)

        other_journal = JournalFactory.create(collection=self.collection)
        subscription_1 = JournalAccessSubscriptionFactory.create(
            user=self.user, journal=self.journal)
        JournalAccessSubscriptionFactory.create(
            user=self.user, journal=other_journal)

        self.client.login(username='david', password='top_secret')
        url = reverse('userspace:journal:subscription:list', kwargs={
            'journal_pk': self.journal.pk, })

        # Run
        response = self.client.get(url)

        # Check
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['subscriptions']), [subscription_1, ])


class TestIndividualJournalAccessSubscriptionCreateView(BaseEruditTestCase):
    def test_cannot_be_accessed_by_a_user_who_cannot_manage_individual_subscriptions(self):
        # Setup
        self.client.login(username='david', password='top_secret')
        url = reverse('userspace:journal:subscription:create', kwargs={
            'journal_pk': self.journal.pk})

        # Run
        response = self.client.get(url)

        # Check
        self.assertEqual(response.status_code, 403)

    def test_can_create_an_account_action_for_the_subscription(self):
        # Setup
        AuthorizationFactory.create(
            content_type=ContentType.objects.get_for_model(self.journal), object_id=self.journal.id,
            user=self.user, authorization_codename=AC.can_manage_individual_subscription.codename)

        plan = JournalManagementPlanFactory.create(max_accounts=10)
        JournalManagementSubscriptionFactory.create(journal=self.journal, plan=plan)

        post_data = {
            'email': faker.email(),
            'first_name': faker.first_name(),
            'last_name': faker.last_name(),
        }

        self.client.login(username='david', password='top_secret')
        url = reverse('userspace:journal:subscription:create', kwargs={
            'journal_pk': self.journal.pk})

        # Run
        response = self.client.post(url, post_data, follow=False)

        # Check
        self.assertEqual(response.status_code, 302)
        tokens = AccountActionToken.objects.all()
        self.assertEqual(tokens.count(), 1)
        stoken = tokens.first()
        self.assertEqual(stoken.content_object, self.journal)
        self.assertEqual(stoken.email, post_data['email'])
        self.assertEqual(stoken.first_name, post_data['first_name'])
        self.assertEqual(stoken.last_name, post_data['last_name'])

    def test_cannot_allow_the_creation_of_subscription_if_the_plan_limit_has_been_reached(self):
        # Setup
        plan = JournalManagementPlanFactory.create(code='test', max_accounts=3)
        JournalManagementSubscriptionFactory.create(journal=self.journal, plan=plan)
        JournalAccessSubscriptionFactory.create(user=self.user, journal=self.journal)
        token_1 = AccountActionTokenFactory.create(content_object=self.journal)
        token_2 = AccountActionTokenFactory.create(content_object=self.journal)  # noqa
        token_1.consume(self.user)

        AuthorizationFactory.create(
            content_type=ContentType.objects.get_for_model(self.journal), object_id=self.journal.id,
            user=self.user, authorization_codename=AC.can_manage_individual_subscription.codename)

        self.client.login(username='david', password='top_secret')
        url = reverse('userspace:journal:subscription:create', kwargs={
            'journal_pk': self.journal.pk})

        # Run
        response = self.client.get(url)

        # Check
        self.assertEqual(response.status_code, 302)

    def test_triggers_the_sending_of_a_notification_email(self):
        # Setup
        AuthorizationFactory.create(
            content_type=ContentType.objects.get_for_model(self.journal), object_id=self.journal.id,
            user=self.user, authorization_codename=AC.can_manage_individual_subscription.codename)

        plan = JournalManagementPlanFactory.create(max_accounts=10)
        JournalManagementSubscriptionFactory.create(journal=self.journal, plan=plan)

        post_data = {
            'email': faker.email(),
            'first_name': faker.first_name(),
            'last_name': faker.last_name(),
        }

        self.client.login(username='david', password='top_secret')
        url = reverse('userspace:journal:subscription:create', kwargs={
            'journal_pk': self.journal.pk})

        # Run
        response = self.client.post(url, post_data, follow=False)

        # Check
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], post_data['email'])


class TestIndividualJournalAccessSubscriptionDeleteView(BaseEruditTestCase):
    def test_cannot_be_accessed_by_a_user_who_cannot_manage_individual_subscriptions(self):
        # Setup
        subscription = JournalAccessSubscriptionFactory.create(
            user=self.user, journal=self.journal)

        self.client.login(username='david', password='top_secret')
        url = reverse('userspace:journal:subscription:delete', kwargs={
            'journal_pk': self.journal.pk, 'pk': subscription.pk, })

        # Run
        response = self.client.get(url)

        # Check
        self.assertEqual(response.status_code, 403)

    def test_can_properly_delete_a_subscription(self):
        # Setup
        AuthorizationFactory.create(
            content_type=ContentType.objects.get_for_model(self.journal), object_id=self.journal.id,
            user=self.user, authorization_codename=AC.can_manage_individual_subscription.codename)

        plan = JournalManagementPlanFactory.create(max_accounts=10)
        JournalManagementSubscriptionFactory.create(journal=self.journal, plan=plan)

        subscription = JournalAccessSubscriptionFactory.create(
            user=self.user, journal=self.journal)

        self.client.login(username='david', password='top_secret')
        url = reverse('userspace:journal:subscription:delete', kwargs={
            'journal_pk': self.journal.pk, 'pk': subscription.pk, })

        # Run
        response = self.client.post(url, follow=False)

        # Check
        self.assertEqual(response.status_code, 302)
        self.assertFalse(JournalAccessSubscription.objects.exists())


class TestIndividualJournalAccessSubscriptionCancelView(BaseEruditTestCase):
    def test_cannot_be_accessed_by_a_user_who_cannot_manage_individual_subscriptions(self):
        # Setup
        token = AccountActionTokenFactory.create(content_object=self.journal)

        self.client.login(username='david', password='top_secret')
        url = reverse('userspace:journal:subscription:cancel', kwargs={
            'journal_pk': self.journal.pk, 'pk': token.pk, })

        # Run
        response = self.client.get(url)

        # Check
        self.assertEqual(response.status_code, 403)

    def test_can_cancel_an_action_token(self):
        # Setup
        AuthorizationFactory.create(
            content_type=ContentType.objects.get_for_model(self.journal), object_id=self.journal.id,
            user=self.user, authorization_codename=AC.can_manage_individual_subscription.codename)

        plan = JournalManagementPlanFactory.create(max_accounts=10)
        JournalManagementSubscriptionFactory.create(journal=self.journal, plan=plan)

        token = AccountActionTokenFactory.create(content_object=self.journal)

        self.client.login(username='david', password='top_secret')
        url = reverse('userspace:journal:subscription:cancel', kwargs={
            'journal_pk': self.journal.pk, 'pk': token.pk, })

        # Run
        response = self.client.post(url, follow=False)

        # Check
        self.assertEqual(response.status_code, 302)
        token.refresh_from_db()
        self.assertFalse(token.active)
