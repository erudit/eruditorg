from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.test import TestCase

from base.test.factories import UserFactory
from base.test.testcases import Client
from erudit.test.factories import OrganisationFactory

from core.authorization.defaults import AuthorizationConfig as AC
from core.authorization.test.factories import AuthorizationFactory
from core.subscription.models import InstitutionIPAddressRange
from core.subscription.test.factories import InstitutionIPAddressRangeFactory
from core.subscription.test.factories import JournalAccessSubscriptionFactory


class TestInstitutionIPAddressRangeListView(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.organisation = OrganisationFactory.create()
        self.user.is_staff = True
        self.user.save()
        self.organisation.members.add(self.user)
        self.subscription = JournalAccessSubscriptionFactory.create(valid=True, organisation=self.organisation)

    def test_cannot_be_accessed_by_a_user_who_is_not_in_the_organisation(self):
        # Setup
        user = UserFactory()
        client = Client(logged_user=user)
        url = reverse('userspace:library:subscription_ips:list', kwargs={
            'organisation_pk': self.organisation.pk, })

        # Run
        response = client.get(url)

        # Check
        self.assertEqual(response.status_code, 403)

    def test_provides_all_the_ip_ranges_for_the_current_organisation(self):
        # Setup
        AuthorizationFactory.create(
            content_type=ContentType.objects.get_for_model(self.organisation),
            object_id=self.organisation.id, user=self.user,
            authorization_codename=AC.can_manage_organisation_subscription_ips.codename)

        ip_range_1 = InstitutionIPAddressRangeFactory.create(
            subscription=self.subscription, ip_start='10.0.0.0', ip_end='11.0.0.0')
        ip_range_2 = InstitutionIPAddressRangeFactory.create(
            subscription=self.subscription, ip_start='20.0.0.0', ip_end='21.0.0.0')

        client = Client(logged_user=self.user)
        url = reverse('userspace:library:subscription_ips:list', kwargs={
            'organisation_pk': self.organisation.pk, })

        # Run
        response = client.get(url)

        # Check
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context['subscription_ip_ranges']), [ip_range_1, ip_range_2, ])


class TestInstitutionIPAddressRangeCreateView(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.organisation = OrganisationFactory.create()
        self.organisation.members.add(self.user)
        self.subscription = JournalAccessSubscriptionFactory.create(valid=True, organisation=self.organisation)

    def test_cannot_be_accessed_by_a_user_who_cannot_manage_subscriptions_ips(self):
        # Setup
        self.organisation.members.clear()
        client = Client(logged_user=self.user)
        url = reverse('userspace:library:subscription_ips:create', kwargs={
            'organisation_pk': self.organisation.pk, })

        # Run
        response = client.get(url)

        # Check
        self.assertEqual(response.status_code, 403)

    def test_can_create_an_ip_range(self):
        # Setup
        user = UserFactory(is_staff=True)

        client = Client(logged_user=user)
        url = reverse('userspace:library:subscription_ips:create', kwargs={
            'organisation_pk': self.organisation.pk, })

        post_data = {
            'ip_start': '10.0.0.0',
            'ip_end': '11.0.0.0',
        }

        # Run
        response = client.post(url, post_data, follow=False)

        # Check
        self.assertEqual(response.status_code, 302)
        ip_range_qs = InstitutionIPAddressRange.objects.filter(subscription=self.subscription)
        self.assertEqual(ip_range_qs.count(), 1)
        self.assertEqual(ip_range_qs.first().ip_start, '10.0.0.0')
        self.assertEqual(ip_range_qs.first().ip_end, '11.0.0.0')


class TestInstitutionIPAddressRangeDeleteView(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.organisation = OrganisationFactory.create()
        self.organisation.members.add(self.user)
        self.subscription = JournalAccessSubscriptionFactory.create(valid=True, organisation=self.organisation)

        self.ip_range = InstitutionIPAddressRangeFactory.create(
            subscription=self.subscription, ip_start='10.0.0.0', ip_end='11.0.0.0')

    def test_cannot_be_accessed_by_a_user_who_cannot_manage_subscriptions_ips(self):
        # Setup
        self.organisation.members.clear()
        client = Client(logged_user=self.user)
        url = reverse('userspace:library:subscription_ips:delete', kwargs={
            'organisation_pk': self.organisation.pk, 'pk': self.ip_range.pk, })

        # Run
        response = client.get(url)

        # Check
        self.assertEqual(response.status_code, 403)

    def test_can_properly_delete_an_ip_range(self):
        # Setup
        user = UserFactory(is_staff=True)

        client = Client(logged_user=user)
        url = reverse('userspace:library:subscription_ips:delete', kwargs={
            'organisation_pk': self.organisation.pk, 'pk': self.ip_range.pk, })

        # Run
        response = client.post(url, follow=False)

        # Check
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            InstitutionIPAddressRange.objects.filter(subscription=self.subscription).exists())
