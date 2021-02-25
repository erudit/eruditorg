# -*- coding: utf-8 -*
import pytest

from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.models import ContentType

from base.test.factories import UserFactory
from erudit.test.factories import JournalFactory, OrganisationFactory

from core.authorization.defaults import AuthorizationConfig as AC
from core.authorization.test.factories import AuthorizationFactory


@pytest.fixture()
def superuser():
    user = UserFactory()
    user.is_superuser = True
    user.save()
    return user


@pytest.fixture()
def staff_user():
    user = UserFactory()
    user.is_staff = True
    user.save()
    return user


@pytest.mark.django_db
class TestUserspaceAccessRule:
    def test_knows_that_an_anonymous_user_cannot_access_the_userspace(self):
        # Run & check
        assert not AnonymousUser().has_perm("userspace.access")

    def test_knows_that_a_superuser_can_access_the_userspace(self, superuser):
        assert superuser.has_perm("userspace.access")

    def test_knows_that_a_staff_user_can_access_the_userspace(self, staff_user):
        assert staff_user.has_perm("userspace.access")

    def test_knows_that_a_user_without_authorization_cannot_access_the_userspace(self):
        assert not UserFactory().has_perm("userspace.access")

    def test_knows_that_a_user_with_the_authorization_management_authorization_can_access_the_userspace(  # noqa
        self,
    ):  # noqa
        # Setup
        user = UserFactory()
        journal = JournalFactory()
        journal.members.add(user)
        AuthorizationFactory.create(
            content_type=ContentType.objects.get_for_model(journal),
            object_id=journal.id,
            user=user,
            authorization_codename=AC.can_manage_authorizations.codename,
        )
        # Run & check
        assert user.has_perm("userspace.access")

    def test_knows_that_a_user_with_the_issuesubmission_management_authorization_can_access_the_userspace(  # noqa
        self,
    ):  # noqa
        # Setup
        user = UserFactory()
        journal = JournalFactory()
        journal.members.add(user)
        AuthorizationFactory.create(
            content_type=ContentType.objects.get_for_model(journal),
            object_id=journal.id,
            user=user,
            authorization_codename=AC.can_manage_issuesubmission.codename,
        )
        # Run & check
        assert user.has_perm("userspace.access")

    def test_knows_that_a_user_with_the_individual_subscription_management_authorization_can_access_the_userspace(  # noqa
        self,
    ):  # noqa
        # Setup
        user = UserFactory()
        journal = JournalFactory()
        journal.members.add(user)
        AuthorizationFactory.create(
            content_type=ContentType.objects.get_for_model(journal),
            object_id=journal.id,
            user=user,
            authorization_codename=AC.can_manage_individual_subscription.codename,
        )
        # Run & check
        assert user.has_perm("userspace.access")

    def test_knows_that_a_user_with_the_journal_information_edit_authorization_can_access_the_userspace(  # noqa
        self,
    ):  # noqa
        # Setup
        user = UserFactory()
        journal = JournalFactory()
        journal.members.add(user)
        AuthorizationFactory.create(
            content_type=ContentType.objects.get_for_model(journal),
            object_id=journal.id,
            user=user,
            authorization_codename=AC.can_edit_journal_information.codename,
        )
        # Run & check
        assert user.has_perm("userspace.access")

    def test_an_organisation_member_can_access_the_userspace(self):
        user = UserFactory()
        organisation = OrganisationFactory()
        organisation.members.add(user)

        assert user.has_perm("userspace.access")
