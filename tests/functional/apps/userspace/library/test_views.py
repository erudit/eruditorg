import pytest

from django.test.client import Client
from django.urls import reverse

from erudit.test.factories import OrganisationFactory
from core.subscription.test.factories import JournalAccessSubscriptionFactory
from base.test.factories import UserFactory


@pytest.mark.django_db
class TestLibraryUserspaceViews:

    @pytest.mark.parametrize('subscription_status_valid', (True, False, None))
    def test_organisation_member_can_access_regardless_of_subscription_status(self, subscription_status_valid):

        member = UserFactory(username='test')
        member.set_password('notsecret')
        member.save()

        organisation = OrganisationFactory()
        organisation.members.add(member)
        organisation.save()

        client = Client()
        client.login(username=member.username, password='notsecret')

        if subscription_status_valid in (True, False):
            JournalAccessSubscriptionFactory(
                valid=subscription_status_valid, organisation=organisation
            )
        url = reverse('userspace:library:home', kwargs={'organisation_pk': organisation.pk})
        resp = client.get(url)
        assert resp.status_code == 200
