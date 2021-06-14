import pytest

from django.contrib.auth.models import AnonymousUser

from erudit.test.factories import OrganisationFactory

from base.test.factories import UserFactory
from core.subscription.test.factories import JournalAccessSubscriptionFactory

from apps.userspace.library.shortcuts import get_managed_organisations, get_last_valid_subscription


@pytest.mark.django_db
class TestGetLastValidSubscriptionShortcut:
    def test_can_return_the_last_valid_subscription(self):
        organisation = OrganisationFactory()
        subscription = JournalAccessSubscriptionFactory(organisation=organisation, post__valid=True)
        assert get_last_valid_subscription(organisation) == subscription

    def test_can_return_the_last_invalid_subscription(self):
        organisation = OrganisationFactory()
        subscription = JournalAccessSubscriptionFactory(organisation=organisation)
        assert get_last_valid_subscription(organisation) == subscription

    def test_can_return_the_last_valid_subscription_even_if_an_invalid_one_is_more_recent(self):
        organisation = OrganisationFactory()
        valid_subscription = JournalAccessSubscriptionFactory(
            organisation=organisation, post__valid=True
        )
        JournalAccessSubscriptionFactory(organisation=organisation)
        assert get_last_valid_subscription(organisation) == valid_subscription


@pytest.mark.django_db
class TestGetManagedOrganisationsShortcut:
    def test_cannot_return_managed_organisations_for_anonymous_users(self):
        # Setup
        OrganisationFactory.create()
        user = AnonymousUser()
        # Run & check
        assert get_managed_organisations(user) is None

    def test_return_all_organisations_for_superusers_and_staff_users(self):
        # Setup
        org_1 = OrganisationFactory.create()
        org_2 = OrganisationFactory.create()
        user_1 = UserFactory.create(is_superuser=True)
        user_2 = UserFactory.create(is_staff=True)
        # Run & check
        assert list(get_managed_organisations(user_1)) == [
            org_1,
            org_2,
        ]
        assert list(get_managed_organisations(user_2)) == [
            org_1,
            org_2,
        ]

    def test_can_return_only_organisations_that_have_the_considered_users_in_their_members(self):
        # Setup
        org_1 = OrganisationFactory.create()
        org_2 = OrganisationFactory.create()
        org_3 = OrganisationFactory.create()
        user = UserFactory.create()
        org_1.members.add(user)
        JournalAccessSubscriptionFactory.create(organisation=org_1)
        JournalAccessSubscriptionFactory.create(organisation=org_2)
        JournalAccessSubscriptionFactory.create(organisation=org_3)
        # Run & check
        assert list(get_managed_organisations(user)) == [
            org_1,
        ]
