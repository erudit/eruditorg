# -*- coding; utf-8 -*-

from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from core.authorization.defaults import AuthorizationConfig as AC
from core.authorization.factories import AuthorizationFactory
from core.subscription.factories import JournalAccessSubscriptionFactory
from core.subscription.models import JournalAccessSubscription
from erudit.factories import JournalFactory
from erudit.tests.base import BaseEruditTestCase


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

        other_journal = JournalFactory.create()
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
