import pytest

import datetime as dt

from django.contrib.contenttypes.models import ContentType

from base.test.factories import UserFactory
from erudit.test.factories import OrganisationFactory, JournalFactory

from core.authorization.defaults import AuthorizationConfig as AC
from core.authorization.test.factories import AuthorizationFactory
from core.subscription.test.factories import JournalAccessSubscriptionFactory
from core.subscription.test.factories import JournalAccessSubscriptionPeriodFactory
from core.subscription.test.factories import JournalManagementPlanFactory
from core.subscription.test.factories import JournalManagementSubscriptionFactory


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
class TestManageIndividualSubscriptionRule:
    def test_knows_that_a_superuser_can_manage_individual_subscriptions(self, superuser):
        assert superuser.has_perm('subscription.manage_individual_subscription', JournalFactory())

    def test_knows_that_a_staff_member_can_manage_individual_subscriptions(self, staff_user):
        # Run & check
        assert staff_user.has_perm('subscription.manage_individual_subscription', JournalFactory())

    def test_knows_if_a_simple_user_can_manage_individual_subscriptions(self):
        # Setup
        journal = JournalFactory()
        user = UserFactory()
        journal.members.add(user)
        AuthorizationFactory.create(
            content_type=ContentType.objects.get_for_model(journal), object_id=journal.id,
            user=user, authorization_codename=AC.can_manage_individual_subscription.codename)
        plan = JournalManagementPlanFactory.create(max_accounts=10)

        JournalManagementSubscriptionFactory.create(journal=journal, plan=plan)
        # Run & check

        assert user.has_perm('subscription.manage_individual_subscription', journal)

    def test_knows_if_a_simple_user_cannot_manage_individual_subscriptions(self):
        user = UserFactory()
        assert not user.has_perm('subscription.manage_individual_subscription', JournalFactory())


@pytest.mark.django_db
class TestManageOrganisationSubscriptionIpsRule:

    def test_knows_that_a_superuser_can_manage_organisation_subscription_ips(self, superuser):
        assert superuser.has_perm('subscription.manage_organisation_subscription_ips', OrganisationFactory())

    def test_knows_that_a_staff_member_can_manage_organisation_subscription_ips(self, staff_user):
        # Setup
        assert staff_user.has_perm('subscription.manage_organisation_subscription_ips', OrganisationFactory())

    def test_knows_if_a_simple_user_can_manage_organisation_subscription_ips(self):
        # Setup
        organisation = OrganisationFactory()
        user = UserFactory()
        AuthorizationFactory.create(
            content_type=ContentType.objects.get_for_model(organisation),
            object_id=organisation.id, user=user,
            authorization_codename=AC.can_manage_organisation_subscription_ips.codename)
        organisation.members.add(user)
        subscription = JournalAccessSubscriptionFactory.create(
            organisation=organisation,
            post__valid=True
        )
        now_dt = dt.datetime.now()
        JournalAccessSubscriptionPeriodFactory.create(
            subscription=subscription,
            start=now_dt - dt.timedelta(days=8),
            end=now_dt + dt.timedelta(days=11))
        # Run & check
        assert user.has_perm('subscription.manage_organisation_subscription_ips', organisation)

    def test_knows_if_a_simple_user_cannot_manage_organisation_subscription_ips(self):
        # Setup
        user = UserFactory()
        assert not user.has_perm('subscription.manage_organisation_subscription_ips', OrganisationFactory())
