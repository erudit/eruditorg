import pytest

from django.urls import reverse
from django.test.client import Client

from erudit.test.factories import OrganisationFactory

from base.test.factories import UserFactory
from core.subscription.test.factories import JournalAccessSubscriptionFactory


@pytest.mark.django_db
class TestCollectionViews:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = Client()

        self.user = UserFactory()

        self.organisation = OrganisationFactory.create()
        self.organisation.members.add(self.user)

        JournalAccessSubscriptionFactory.create(organisation=self.organisation, post__valid=True)

    def test_cannot_be_accessed_by_a_user_who_cannot_manage_collection_information(self):
        # Setup
        self.organisation.members.clear()
        self.client.login(username=self.user.username, password="default")

        url = reverse(
            "userspace:library:collection:landing",
            kwargs={
                "organisation_pk": self.organisation.pk,
            },
        )

        # Run
        response = self.client.get(url)

        # Check
        assert response.status_code == 403

    def test_can_be_accessed_by_an_organisation_member(self):
        self.client.login(username=self.user.username, password="default")

        url = reverse(
            "userspace:library:collection:landing",
            kwargs={
                "organisation_pk": self.organisation.pk,
            },
        )

        # Run
        response = self.client.get(url)

        # Check
        assert response.status_code == 200
