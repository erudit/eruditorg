import datetime as dt
import io
from unittest.mock import Mock

import pytest
from account_actions.models import AccountActionToken
from account_actions.test.factories import AccountActionTokenFactory
from django.conf import settings
from django.core import mail
from django.urls import reverse
from django.test import TestCase
from faker import Factory

from base.test.factories import UserFactory
from base.test.testcases import Client
from erudit.test.factories import JournalFactory

from core.authorization.defaults import AuthorizationConfig as AC
from core.authorization.models import Authorization
from core.subscription.models import JournalAccessSubscription, JournalManagementSubscription
from core.subscription.account_actions import IndividualSubscriptionAction
from core.subscription.test.factories import JournalAccessSubscriptionFactory
from core.subscription.test.factories import JournalManagementPlanFactory
from core.subscription.test.factories import JournalManagementSubscriptionFactory
from core.victor import Victor

from apps.userspace.journal.subscription import views

faker = Factory.create()

pytestmark = pytest.mark.django_db

# Helpers


def journal_that_can_subscribe():
    # Return a (Journal, User) that has a proper subscription plan and proper authorisations.
    # This pair is ready to use in subscription views.
    user = UserFactory.create()
    journal = JournalFactory.create(members=[user])
    JournalManagementSubscriptionFactory.create(journal=journal)
    Authorization.authorize_user(user, journal, AC.can_manage_individual_subscription)
    Authorization.authorize_user(user, journal, AC.can_manage_institutional_subscription)
    return journal, user


# Tests

def test_list_cannot_be_accessed_by_a_member_without_permission():
    user = UserFactory.create()
    journal = JournalFactory.create(members=[user])
    JournalManagementSubscriptionFactory.create(journal=journal)
    client = Client()
    client.login(username=user.username, password="default")

    url = reverse('userspace:journal:subscription:list', kwargs={
        'journal_pk': journal.pk, })
    response = client.get(url)

    assert response.status_code == 403


def test_list_can_be_accessed_by_a_member_with_permission():
    user = UserFactory.create()
    journal = JournalFactory.create(members=[user])
    JournalManagementSubscriptionFactory.create(journal=journal)

    Authorization.authorize_user(user, journal, AC.can_manage_individual_subscription)

    client = Client()
    client.login(username=user.username, password="default")

    url = reverse('userspace:journal:subscription:list', kwargs={
        'journal_pk': journal.pk, })
    response = client.get(url)

    assert response.status_code == 200


def test_list_cannot_be_accessed_by_a_non_member():
    user = UserFactory()
    journal = JournalFactory()

    client = Client()
    client.login(username=user.username, password='default')
    url = reverse('userspace:journal:subscription:list', kwargs={
        'journal_pk': journal.pk, })

    response = client.get(url)

    assert response.status_code == 403


def test_list_provides_only_subscriptions_associated_with_the_current_journal():
    user = UserFactory.create()
    journal = JournalFactory.create(members=[user])
    Authorization.authorize_user(user, journal, AC.can_manage_individual_subscription)

    plan = JournalManagementPlanFactory.create()
    management_subscription = JournalManagementSubscriptionFactory.create(
        journal=journal, plan=plan)

    other_journal = JournalFactory.create(collection=journal.collection)
    subscription_1 = JournalAccessSubscriptionFactory.create(
        user=user, journals=[journal], journal_management_subscription=management_subscription)
    JournalAccessSubscriptionFactory.create(
        user=user, journals=[other_journal])

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

    journal, user = journal_that_can_subscribe()

    archive_subpath = views.JournalOrganisationSubscriptionList.ARCHIVE_SUBPATH
    subdir = tmpdir.join(str(journal.code), archive_subpath).ensure(dir=True)

    ARCHIVE_YEARS = ['2012', '1830', '2016']
    for year in ARCHIVE_YEARS:
        subdir.join('{}.csv'.format(year)).write('hello')

    client = Client()
    client.login(username=user.username, password='default')

    url = reverse('userspace:journal:subscription:org_list')
    response = client.get(url, follow=True)
    view = response.context['view']

    EXPECTED = [(str(dt.date.today().year), reverse('userspace:journal:subscription:org_export'))]
    for year in sorted(ARCHIVE_YEARS, reverse=True):
        url = reverse('userspace:journal:subscription:org_export_download')
        url += '?subpath={}/{}.csv'.format(archive_subpath, year)
        EXPECTED.append((year, url))
    assert view.get_subscriptions_archive_years() == EXPECTED


class TestIndividualJournalAccessSubscriptionCreateView(TestCase):
    def test_cannot_be_accessed_by_a_user_who_cannot_manage_individual_subscriptions(self):
        journal = JournalFactory()
        client = Client(logged_user=UserFactory())
        url = reverse('userspace:journal:subscription:create', kwargs={
            'journal_pk': journal.pk})

        # Run
        response = client.get(url)

        # Check
        self.assertEqual(response.status_code, 403)

    def test_can_create_an_account_action_for_the_subscription(self):
        journal = JournalFactory()
        user = UserFactory()
        journal.members.add(user)
        Authorization.authorize_user(
            user, journal, AC.can_manage_individual_subscription)

        plan = JournalManagementPlanFactory.create(max_accounts=10)
        subscription = JournalManagementSubscriptionFactory.create(journal=journal, plan=plan)

        post_data = {
            'email': faker.email(),
            'first_name': faker.first_name(),
            'last_name': faker.last_name(),
        }

        client = Client(logged_user=user)
        url = reverse('userspace:journal:subscription:create', kwargs={
            'journal_pk': journal.pk})

        response = client.post(url, post_data, follow=False)

        self.assertEqual(response.status_code, 302)
        tokens = AccountActionToken.objects.all()
        self.assertEqual(tokens.count(), 1)
        stoken = tokens.first()
        self.assertEqual(stoken.content_object, subscription)
        self.assertEqual(stoken.email, post_data['email'])
        self.assertEqual(stoken.first_name, post_data['first_name'])
        self.assertEqual(stoken.last_name, post_data['last_name'])

    def test_cannot_allow_the_creation_of_subscription_if_the_plan_limit_has_been_reached(self):
        journal = JournalFactory()
        user = UserFactory()
        journal.members.add(user)
        subscription = JournalManagementSubscriptionFactory.create(
            journal=journal, plan__max_accounts=3)

        JournalAccessSubscriptionFactory.create(
            user=user, journal_management_subscription=subscription)
        token_1 = AccountActionTokenFactory.create(content_object=subscription)
        AccountActionTokenFactory.create(content_object=subscription)  # noqa

        IndividualSubscriptionAction().execute(token_1)
        token_1.consume(user)

        Authorization.authorize_user(
            user, journal, AC.can_manage_individual_subscription)

        client = Client(logged_user=user)
        url = reverse('userspace:journal:subscription:create', kwargs={
            'journal_pk': journal.pk})

        response = client.get(url)

        self.assertEqual(response.status_code, 302)

    def test_triggers_the_sending_of_a_notification_email(self):
        journal = JournalFactory()
        user = UserFactory()
        journal.members.add(user)
        Authorization.authorize_user(
            user, journal, AC.can_manage_individual_subscription)

        plan = JournalManagementPlanFactory.create(max_accounts=10)
        JournalManagementSubscriptionFactory.create(journal=journal, plan=plan)

        post_data = {
            'email': faker.email(),
            'first_name': faker.first_name(),
            'last_name': faker.last_name(),
        }

        client = Client(logged_user=user)
        url = reverse('userspace:journal:subscription:create', kwargs={
            'journal_pk': journal.pk})

        # Run
        response = client.post(url, post_data, follow=False)

        # Check
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], post_data['email'])


class TestIndividualJournalAccessSubscriptionDeleteView:
    def test_cannot_be_accessed_by_a_user_who_cannot_manage_individual_subscriptions(self):
        user = UserFactory.create()
        journal = JournalFactory.create(members=[user])
        subscription = JournalAccessSubscriptionFactory.create(
            user=user, journals=[journal])

        client = Client()
        client.login(username=user.username, password='default')
        url = reverse('userspace:journal:subscription:delete', kwargs={
            'journal_pk': journal.pk, 'pk': subscription.pk, })

        response = client.get(url)
        assert response.status_code == 403

    def test_can_properly_delete_a_subscription(self):
        user = UserFactory.create()
        journal = JournalFactory.create(members=[user])
        Authorization.authorize_user(user, journal, AC.can_manage_individual_subscription)

        journalsub = JournalManagementSubscriptionFactory.create(journal=journal)
        subscription = JournalAccessSubscriptionFactory.create(
            user=user, journal_management_subscription=journalsub)

        client = Client()
        client.login(username=user.username, password='default')
        url = reverse('userspace:journal:subscription:delete', kwargs={
            'journal_pk': journal.pk, 'pk': subscription.pk, })

        response = client.post(url, follow=False)
        assert response.status_code == 302
        assert not JournalAccessSubscription.objects.exists()


class TestIndividualJournalAccessSubscriptionCancelView(TestCase):
    def test_cannot_be_accessed_by_a_user_who_cannot_manage_individual_subscriptions(self):
        # Setup
        journal = JournalFactory()
        user = UserFactory()
        journal.members.add(user)
        token = AccountActionTokenFactory.create(content_object=journal)

        client = Client(logged_user=user)
        url = reverse('userspace:journal:subscription:cancel', kwargs={
            'journal_pk': journal.pk, 'pk': token.pk, })

        # Run
        response = client.get(url)

        # Check
        self.assertEqual(response.status_code, 403)

    def test_can_cancel_an_action_token(self):
        journal = JournalFactory()
        user = UserFactory()
        journal.members.add(user)
        Authorization.authorize_user(
            user, journal, AC.can_manage_individual_subscription)

        plan = JournalManagementPlanFactory.create(max_accounts=10)
        JournalManagementSubscriptionFactory.create(journal=journal, plan=plan)

        token = AccountActionTokenFactory.create(content_object=journal)

        client = Client(logged_user=user)
        url = reverse('userspace:journal:subscription:cancel', kwargs={
            'journal_pk': journal.pk, 'pk': token.pk, })

        response = client.post(url, follow=False)

        self.assertEqual(response.status_code, 302)
        token.refresh_from_db()
        self.assertFalse(token.active)

# Batch subscribe


def hit_batch_subscribe_with_csv_and_test(
        user, journal, csvlines, expected_toadd, expected_ignored, expected_errors):
    fp = io.BytesIO('\n'.join(csvlines).encode())
    client = Client()
    client.login(username=user.username, password='default')
    url = reverse('userspace:journal:subscription:batch_subscribe', args=[journal.pk])
    response = client.post(url, {'csvfile': fp}, follow=True)

    assert response.status_code == 200
    assert response.context['toadd'] == expected_toadd
    assert response.context['ignored'] == expected_ignored
    assert response.context['errors'] == expected_errors


def test_batch_subscribe_csv_validation_ignored():
    # We ignore emails that are already subscribed
    journal, user = journal_that_can_subscribe()
    foouser = UserFactory.create(email='foo@example.com')
    JournalAccessSubscriptionFactory.create(user=foouser, journals=[journal])
    lines = ['foo@example.com;Foo;Bar']
    hit_batch_subscribe_with_csv_and_test(
        user, journal, lines, [], ['foo@example.com'], [])


def test_batch_subscribe_csv_validation_toadd():
    journal, user = journal_that_can_subscribe()
    lines = ['foo@example.com;Foo;Bar']
    hit_batch_subscribe_with_csv_and_test(
        user, journal, lines, [('foo@example.com', 'Foo', 'Bar')], [], [])


def test_batch_subscribe_csv_validation_toadd_and_ignored():
    journal, user = journal_that_can_subscribe()
    foouser = UserFactory.create(email='foo@example.com')
    JournalAccessSubscriptionFactory.create(user=foouser, journals=[journal])
    lines = ['foo@example.com;Foo;Bar', 'other@example.com;Other;Name']
    hit_batch_subscribe_with_csv_and_test(
        user, journal, lines, [('other@example.com', 'Other', 'Name')],
        ['foo@example.com'], [])


def test_batch_subscribe_csv_validation_errors():
    journal, user = journal_that_can_subscribe()
    lines = [
        'foo@example.com;Foo;Bar',
        'other@example.com;notenoughcolumns',
        'notanemail;foo;bar']
    hit_batch_subscribe_with_csv_and_test(
        user, journal, lines, [], [], [(2, lines[1]), (3, lines[2])])


def test_batch_subscribe_over_limit():
    # When submitting a CSV that has too many lines (go over the plan's limit), we do nothing and
    # display a message.
    journal, user = journal_that_can_subscribe()
    plan = JournalManagementSubscription.objects.get(journal=journal).plan
    plan.max_accounts = 1
    plan.save()
    csvlines = [
        'foo@example.com;Foo;Bar',
        'other@example.com;Other;Name']
    fp = io.BytesIO('\n'.join(csvlines).encode())
    client = Client()
    client.login(username=user.username, password='default')
    url = reverse('userspace:journal:subscription:batch_subscribe', args=[journal.pk])
    response = client.post(url, {'csvfile': fp}, follow=True)
    assert len(response.context['messages']) == 1


def test_batch_subscribe_send_email_proceed():
    journal, user = journal_that_can_subscribe()
    lines = [
        'foo@example.com;Foo;Bar',
        'other@example.com;Other;Name']
    client = Client()
    client.login(username=user.username, password='default')
    url = reverse('userspace:journal:subscription:batch_subscribe', args=[journal.pk])
    response = client.post(url, {'toadd': lines, 'send_email': True}, follow=True)

    assert response.status_code == 200
    assert AccountActionToken.objects.count() == len(lines)


def test_batch_subscribe_directly_proceed():
    journal, user = journal_that_can_subscribe()
    lines = [
        'foo@example.com;Foo;Bar',
        'other@example.com;Other;Name']
    client = Client()
    client.login(username=user.username, password='default')
    url = reverse('userspace:journal:subscription:batch_subscribe', args=[journal.pk])
    response = client.post(url, {'toadd': lines}, follow=True)

    assert response.status_code == 200
    assert JournalAccessSubscription.objects.count() == len(lines)


# Batch delete
def hit_batch_delete_with_csv_and_test(
        user, journal, csvlines, expected_todelete, expected_ignored, expected_errors):
    fp = io.BytesIO('\n'.join(csvlines).encode())
    client = Client()
    client.login(username=user.username, password='default')
    url = reverse('userspace:journal:subscription:batch_delete', args=[journal.pk])
    response = client.post(url, {'csvfile': fp}, follow=True)

    assert response.status_code == 200
    assert response.context['todelete'] == expected_todelete
    assert response.context['ignored'] == expected_ignored
    assert response.context['errors'] == expected_errors


def test_batch_delete_csv_validation_ignored():
    # We ignore emails that aren't subscribed
    journal, user = journal_that_can_subscribe()
    lines = ['foo@example.com']
    hit_batch_delete_with_csv_and_test(
        user, journal, lines, [], lines, [])


def test_batch_delete_csv_validation_todelete():
    journal, user = journal_that_can_subscribe()
    foouser = UserFactory.create(email='foo@example.com')
    sub = JournalAccessSubscriptionFactory.create(user=foouser, journals=[journal])
    lines = ['foo@example.com']
    hit_batch_delete_with_csv_and_test(
        user, journal, lines, [sub], [], [])


def test_batch_delete_csv_validation_todelete_and_ignored():
    journal, user = journal_that_can_subscribe()
    foouser = UserFactory.create(email='foo@example.com')
    sub = JournalAccessSubscriptionFactory.create(user=foouser, journals=[journal])
    lines = ['foo@example.com', 'other@example.com']
    hit_batch_delete_with_csv_and_test(
        user, journal, lines, [sub], ['other@example.com'], [])


def test_batch_delete_csv_validation_errors():
    journal, user = journal_that_can_subscribe()
    foouser = UserFactory.create(email='foo@example.com')
    JournalAccessSubscriptionFactory.create(user=foouser, journals=[journal])
    lines = ['foo@example.com', 'other@example.com', 'notanemail']
    hit_batch_delete_with_csv_and_test(
        user, journal, lines, [], [], [(3, 'notanemail')])


def test_batch_delete_ignore_trailing_delimiter():
    # The input being a CSV, it's possible that it contains a trailing delimiter. If it does,
    # ignore it and properly parse addresses.
    # We ignore emails that aren't subscribed
    journal, user = journal_that_can_subscribe()
    lines = ['foo@example.com;', '"bar@example.com";']
    hit_batch_delete_with_csv_and_test(
        user, journal, lines, [], ['foo@example.com', 'bar@example.com'], [])


def test_batch_delete_proceed():
    journal, user = journal_that_can_subscribe()
    foouser = UserFactory.create(email='foo@example.com')
    sub = JournalAccessSubscriptionFactory.create(user=foouser, journals=[journal])
    client = Client()
    client.login(username=user.username, password='default')
    url = reverse('userspace:journal:subscription:batch_delete', args=[journal.pk])
    response = client.post(url, {'todelete': [sub.pk]}, follow=True)

    assert response.status_code == 200
    assert not JournalAccessSubscription.objects.exists()



@pytest.mark.parametrize('should_be_in_export,should_not_be_in_export', [
    (dict(Id='42', InstitutionName='Foo'), dict(NotThere='Bar')),
    (dict(), dict())
])
def test_subscription_live_report_contents(
    monkeypatch,
    should_be_in_export,
    should_not_be_in_export):
    # Asking for current year returns live results from Victor

    class MockedVictor:
        def get_subscriber_contact_informations(self, product_name):
            assert product_name == journal.code
            victor_data = should_be_in_export.copy()
            victor_data.update(should_not_be_in_export)
            return [Mock(**victor_data)]

    journal, user = journal_that_can_subscribe()

    monkeypatch.setattr(Victor, 'get_configured_instance', lambda: MockedVictor())

    client = Client()
    client.login(username=user.username, password='default')

    url = reverse('userspace:journal:subscription:org_export')
    response = client.get(url, follow=True)

    for key in should_be_in_export.keys():
        assert should_be_in_export[key].encode('utf-8') in response.content

    for key in should_not_be_in_export.keys():
        assert should_not_be_in_export[key].encode('utf-8') not in response.content

