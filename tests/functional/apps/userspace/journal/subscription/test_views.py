import datetime as dt
import pytest
from account_actions.models import AccountActionToken
from account_actions.test.factories import AccountActionTokenFactory
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.core import mail
from django.core.urlresolvers import reverse
from django.test.client import Client
from faker import Factory

from base.test.factories import UserFactory

from erudit.test import BaseEruditTestCase
from erudit.test.factories import JournalFactory

from core.authorization.defaults import AuthorizationConfig as AC
from core.authorization.test.factories import AuthorizationFactory
from core.subscription.models import JournalAccessSubscription
from core.subscription.account_actions import IndividualSubscriptionAction
from core.subscription.test.factories import JournalAccessSubscriptionFactory
from core.subscription.test.factories import JournalManagementPlanFactory
from core.subscription.test.factories import JournalManagementSubscriptionFactory
from core.victor import Victor

from apps.userspace.journal.subscription import views

faker = Factory.create()

pytestmark = pytest.mark.django_db

def test_list_cannot_be_accessed_by_a_member_without_permission():
    user = UserFactory(password="test")
    journal = JournalFactory()
    journal.members.add(user)
    journal.save()

    client = Client()
    client.login(username=user.username, password="test")

    url = reverse('userspace:journal:subscription:list', kwargs={
        'journal_pk': journal.pk, })
    response = client.get(url)

    assert response.status_code == 403


def test_list_can_be_accessed_by_a_member_with_permission():
    user = UserFactory(password="test")
    journal = JournalFactory()
    journal.members.add(user)
    journal.save()

    AuthorizationFactory.create(
        content_type=ContentType.objects.get_for_model(journal), object_id=journal.id,
        user=user, authorization_codename=AC.can_manage_institutional_subscription.codename)

    client = Client()
    client.login(username=user.username, password="test")

    url = reverse('userspace:journal:subscription:list', kwargs={
        'journal_pk': journal.pk, })
    response = client.get(url)

    assert response.status_code == 200


def test_list_cannot_be_accessed_by_a_non_member():
    user = UserFactory(password="test")
    journal = JournalFactory()

    client = Client()
    client.login(username=user.username, password='test')
    url = reverse('userspace:journal:subscription:list', kwargs={
        'journal_pk': journal.pk, })

    response = client.get(url)

    assert response.status_code == 403

def test_list_provides_only_subscriptions_associated_with_the_current_journal():
    user = UserFactory.create()
    journal = JournalFactory.create(members=[user])
    AuthorizationFactory.create(
        content_type=ContentType.objects.get_for_model(journal), object_id=journal.id,
        user=user, authorization_codename=AC.can_manage_institutional_subscription.codename)

    plan = JournalManagementPlanFactory.create(max_accounts=10)
    management_subscription = JournalManagementSubscriptionFactory.create(journal=journal, plan=plan)

    other_journal = JournalFactory.create(collection=journal.collection)
    subscription_1 = JournalAccessSubscriptionFactory.create(
        user=user, journal=journal, journal_management_subscription=management_subscription)
    JournalAccessSubscriptionFactory.create(
        user=user, journal=other_journal)

    client = Client()
    client.login(username=user.username, password='default')
    url = reverse('userspace:journal:subscription:list', kwargs={
        'journal_pk': journal.pk, })

    response = client.get(url)

    assert response.status_code == 200
    assert list(response.context['subscriptions']) == [subscription_1, ]

def test_list_archive_years(monkeypatch, tmpdir):
    # The subscription list view lists available years for subscription exports.
    monkeypatch.setattr(settings, 'SUBSCRIPTION_EXPORTS_ROOT', str(tmpdir))

    user = UserFactory.create()
    journal = JournalFactory.create(members=[user])
    journal.members.add(user)

    AuthorizationFactory.create(
        content_type=ContentType.objects.get_for_model(journal), object_id=journal.id,
        user=user, authorization_codename=AC.can_manage_institutional_subscription.codename)

    archive_subpath = views.IndividualJournalAccessSubscriptionListView.ARCHIVE_SUBPATH
    subdir = tmpdir.join(str(journal.code), archive_subpath).ensure(dir=True)

    ARCHIVE_YEARS = ['2012', '1830', '2016']
    for year in ARCHIVE_YEARS:
        subdir.join('{}.csv'.format(year)).write('hello')

    client = Client()
    client.login(username=user.username, password='default')

    url = reverse('userspace:journal:subscription:list')
    response = client.get(url, follow=True)
    view = response.context['view']

    EXPECTED = [(str(dt.date.today().year), reverse('userspace:journal:subscription:org_export'))]
    for year in sorted(ARCHIVE_YEARS, reverse=True):
        url = reverse('userspace:journal:reports_download')
        url += '?subpath={}/{}.csv'.format(archive_subpath, year)
        EXPECTED.append((year, url))
    assert view.get_subscriptions_archive_years() == EXPECTED


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
        subscription = JournalManagementSubscriptionFactory.create(journal=self.journal, plan=plan)

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
        self.assertEqual(stoken.content_object, subscription)
        self.assertEqual(stoken.email, post_data['email'])
        self.assertEqual(stoken.first_name, post_data['first_name'])
        self.assertEqual(stoken.last_name, post_data['last_name'])

    def test_cannot_allow_the_creation_of_subscription_if_the_plan_limit_has_been_reached(self):
        # Setup

        subscription = JournalManagementSubscriptionFactory.create(journal=self.journal, plan__max_accounts=3)

        JournalAccessSubscriptionFactory.create(user=self.user, journal_management_subscription=subscription)
        token_1 = AccountActionTokenFactory.create(content_object=subscription)
        token_2 = AccountActionTokenFactory.create(content_object=subscription)  # noqa


        IndividualSubscriptionAction().execute(token_1)
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


def test_subscription_live_report_contents(monkeypatch):
    # Asking for current year returns live results from Victor

    class Result:
        Id = '42'
        InstitutionName = 'Foo'
        NotThere = 'Bar'
        # let's not bother with the whole shebang...

    class MockedVictor:
        def get_subscriber_contact_informations(self, product_name):
            assert product_name == journal.code
            return [Result]

    user = UserFactory.create()
    journal = JournalFactory.create(members=[user])

    monkeypatch.setattr(Victor, 'get_configured_instance', lambda: MockedVictor())

    client = Client()
    client.login(username=user.username, password='default')

    url = reverse('userspace:journal:subscription:org_export')
    response = client.get(url, follow=True)
    assert b'42' in response.content
    assert b'Foo' in response.content
    assert b'Bar' not in response.content
