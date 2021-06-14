import pytest

import datetime as dt
import ipaddress

from django.core.exceptions import ValidationError

from account_actions.test.factories import AccountActionTokenFactory

from erudit.test.factories import OrganisationFactory, JournalFactory

from base.test.factories import UserFactory

from core.subscription.models import JournalAccessSubscription
from core.subscription.test.factories import InstitutionIPAddressRangeFactory
from core.subscription.test.factories import JournalAccessSubscriptionFactory
from core.subscription.test.factories import JournalAccessSubscriptionPeriodFactory
from core.subscription.test.factories import JournalManagementPlanFactory
from core.subscription.test.factories import JournalManagementSubscriptionFactory
from core.subscription.test.factories import JournalManagementSubscriptionPeriodFactory
from core.subscription.test.factories import AccessBasketFactory


@pytest.mark.django_db
class TestJournalAccessSubscription:
    def test_knows_if_it_is_ongoing_or_not(self):
        # Setup
        now_dt = dt.datetime.now()
        subscription_1 = JournalAccessSubscriptionFactory.create()
        subscription_2 = JournalAccessSubscriptionFactory.create()
        JournalAccessSubscriptionPeriodFactory.create(
            subscription=subscription_1,
            start=now_dt - dt.timedelta(days=10),
            end=now_dt + dt.timedelta(days=8),
        )
        JournalAccessSubscriptionPeriodFactory.create(
            subscription=subscription_2,
            start=now_dt + dt.timedelta(days=10),
            end=now_dt + dt.timedelta(days=8),
        )
        # Run & check
        assert subscription_1.is_ongoing
        assert not subscription_2.is_ongoing

    def test_knows_it_is_an_individual_subscription(self):
        subscription = JournalAccessSubscriptionFactory(user=UserFactory(), organisation=None)
        assert subscription.get_subscription_type() == JournalAccessSubscription.TYPE_INDIVIDUAL

    def test_knows_it_is_an_institutional_subscription(self):
        subscription = JournalAccessSubscriptionFactory(
            organisation=OrganisationFactory(), user=None
        )
        assert subscription.get_subscription_type() == JournalAccessSubscription.TYPE_INSTITUTIONAL

    def test_knows_its_underlying_journals(self):
        journal_1, journal_2, journal_3 = JournalFactory.create_batch(3)
        basket = AccessBasketFactory(journals=[journal_1])
        subscription = JournalAccessSubscriptionFactory(basket=basket, journals=[journal_2])
        subscription.journals.add(journal_3)
        assert list(subscription.get_journals()) == [journal_1, journal_2, journal_3]

    def test_basket_provides_access(self):
        j1, j2, j3 = JournalFactory.create_batch(3)
        basket = AccessBasketFactory.create(journals=[j1, j2])
        sub = JournalAccessSubscriptionFactory.create(basket=basket)
        assert sub.provides_access_to(journal=j1)
        assert sub.provides_access_to(journal=j2)
        assert not sub.provides_access_to(journal=j3)

    @pytest.mark.parametrize("subscription_referer", ("https://erudit.org",))
    @pytest.mark.parametrize(
        "user_referer",
        ("https://www.erudit.org", "http://www.erudit.org", "http://www.erudit.org/some/path"),
    )
    def test_can_find_an_institution_referer_by_netloc(self, user_referer, subscription_referer):
        subscription = JournalAccessSubscriptionFactory(
            post__valid=True, referer=subscription_referer
        )
        assert JournalAccessSubscription.valid_objects.get_for_referer(user_referer) == subscription

    @pytest.mark.parametrize(
        "referer,should_find",
        [
            ("http://www.topsecurity.org/bulletproofauthenticationmechanism", True),
            ("http://www.topsecurity.org/", False),
            ("http://proxy.www.topsecurity.org", True),
            ("http://www.topsecurity.org/bulletproofauthenticationmechanism/journal123", True),
        ],
    )
    def test_can_find_an_institution_referer_by_netloc_and_path(self, referer, should_find):
        subscription = JournalAccessSubscriptionFactory(post__valid=True, referer=referer)
        assert (
            JournalAccessSubscription.valid_objects.get_for_referer(referer) == subscription
            or not should_find
        )

    @pytest.mark.parametrize(
        "referer",
        (
            "http://externalservice.com:2049/login?url='allo'",
            "https://externalservice.com:2049/login?url='allo'",
        ),
    )
    def test_can_find_an_institution_referer_with_netloc_port_path_and_querystring(self, referer):
        subscription = JournalAccessSubscriptionFactory(post__valid=True, referer=referer)
        assert JournalAccessSubscription.valid_objects.get_for_referer(referer) == subscription

    def test_can_only_find_institution_referer_when_path_fully_match(self):
        JournalAccessSubscriptionFactory(
            post__valid=True, referer="http://www.erudit.org.proxy.com/"
        )
        assert not JournalAccessSubscription.valid_objects.get_for_referer("http://www.erudit.org/")


@pytest.mark.django_db
class TestUserSubscriptions:
    def test_the_first_subscription_is_the_active_subscription(self):
        from core.subscription.models import UserSubscriptions

        subs = UserSubscriptions()
        subscription = JournalAccessSubscriptionFactory()
        subs.add_subscription(subscription)
        assert subs.active_subscription == subscription


@pytest.mark.django_db
class TestInstitutionIPAddressRange:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.organisation = OrganisationFactory.create()
        self.subscription = JournalAccessSubscriptionFactory(organisation=self.organisation)

    def test_cannot_be_saved_with_an_incoherent_ip_range(self):
        # Run & check
        with pytest.raises(ValidationError):
            ip_range = InstitutionIPAddressRangeFactory.build(
                subscription=self.subscription, ip_start="192.168.1.3", ip_end="192.168.1.2"
            )
            ip_range.clean()

    def test_can_return_the_list_of_corresponding_ip_addresses(self):
        # Setup
        ip_range = InstitutionIPAddressRangeFactory.build(
            subscription=self.subscription, ip_start="192.168.1.3", ip_end="192.168.1.5"
        )
        # Run
        ip_addresses = ip_range.ip_addresses
        # Check
        assert ip_addresses == [
            ipaddress.ip_address("192.168.1.3"),
            ipaddress.ip_address("192.168.1.4"),
            ipaddress.ip_address("192.168.1.5"),
        ]


@pytest.mark.django_db
class TestJournalAccessSubscriptionPeriod:
    def test_cannot_clean_an_incoherent_period(self):
        # Setup
        now_dt = dt.datetime.now()
        subscription = JournalAccessSubscriptionFactory.create()
        period = JournalAccessSubscriptionPeriodFactory.build(
            subscription=subscription,
            start=now_dt + dt.timedelta(days=10),
            end=now_dt + dt.timedelta(days=8),
        )
        # Run & check
        with pytest.raises(ValidationError):
            period.clean()

    def test_cannot_clean_a_period_that_has_a_larger_concurrent_period(self):
        # Setup
        now_dt = dt.datetime.now()
        subscription = JournalAccessSubscriptionFactory.create()
        JournalAccessSubscriptionPeriodFactory.create(
            subscription=subscription,
            start=now_dt + dt.timedelta(days=8),
            end=now_dt + dt.timedelta(days=14),
        )
        period = JournalAccessSubscriptionPeriodFactory.build(
            subscription=subscription,
            start=now_dt + dt.timedelta(days=10),
            end=now_dt + dt.timedelta(days=12),
        )
        # Run & check
        with pytest.raises(ValidationError):
            period.clean()

    def test_cannot_clean_a_period_that_has_an_inner_concurrent_period(self):
        # Setup
        now_dt = dt.datetime.now()
        subscription = JournalAccessSubscriptionFactory.create()
        JournalAccessSubscriptionPeriodFactory.create(
            subscription=subscription,
            start=now_dt + dt.timedelta(days=9),
            end=now_dt + dt.timedelta(days=11),
        )
        period = JournalAccessSubscriptionPeriodFactory.build(
            subscription=subscription,
            start=now_dt + dt.timedelta(days=8),
            end=now_dt + dt.timedelta(days=14),
        )
        # Run & check
        with pytest.raises(ValidationError):
            period.clean()

    def test_cannot_clean_a_period_that_has_an_older_concurrent_period(self):
        # Setup
        now_dt = dt.datetime.now()
        subscription = JournalAccessSubscriptionFactory.create()
        JournalAccessSubscriptionPeriodFactory.create(
            subscription=subscription,
            start=now_dt + dt.timedelta(days=8),
            end=now_dt + dt.timedelta(days=11),
        )
        period = JournalAccessSubscriptionPeriodFactory.build(
            subscription=subscription,
            start=now_dt + dt.timedelta(days=10),
            end=now_dt + dt.timedelta(days=12),
        )
        # Run & check
        with pytest.raises(ValidationError):
            period.clean()

    def test_cannot_clean_a_period_that_has_a_younger_concurrent_period(self):
        # Setup
        now_dt = dt.datetime.now()
        subscription = JournalAccessSubscriptionFactory.create()
        JournalAccessSubscriptionPeriodFactory.create(
            subscription=subscription,
            start=now_dt + dt.timedelta(days=11),
            end=now_dt + dt.timedelta(days=15),
        )
        period = JournalAccessSubscriptionPeriodFactory.build(
            subscription=subscription,
            start=now_dt + dt.timedelta(days=10),
            end=now_dt + dt.timedelta(days=12),
        )
        # Run & check
        with pytest.raises(ValidationError):
            period.clean()


@pytest.mark.django_db
class TestJournalManagementSubscription:
    def test_knows_if_it_is_ongoing_or_not(self):
        # Setup
        journal = JournalFactory()
        now_dt = dt.datetime.now()
        plan = JournalManagementPlanFactory.create(max_accounts=10)

        subscription_1 = JournalManagementSubscriptionFactory.create(journal=journal, plan=plan)
        subscription_2 = JournalManagementSubscriptionFactory.create(journal=journal, plan=plan)

        JournalManagementSubscriptionPeriodFactory.create(
            subscription=subscription_1,
            start=now_dt - dt.timedelta(days=10),
            end=now_dt + dt.timedelta(days=8),
        )
        JournalManagementSubscriptionPeriodFactory.create(
            subscription=subscription_2,
            start=now_dt + dt.timedelta(days=10),
            end=now_dt + dt.timedelta(days=8),
        )
        # Run & check
        assert subscription_1.is_ongoing
        assert not subscription_2.is_ongoing

    @pytest.mark.parametrize(
        "email,firstname,lastname",
        (
            ("test@test.com", "First", "Name"),
            ("test2@test.com", None, None),
        ),
    )
    def test_can_subscribe_email(self, email, firstname, lastname):
        plan = JournalManagementPlanFactory(is_unlimited=True)
        subscription = JournalManagementSubscriptionFactory.create(plan=plan)
        subscription.subscribe_email(email, first_name=firstname, last_name=lastname)

        assert JournalAccessSubscription.objects.filter(
            user__first_name=firstname if firstname else "",
            user__last_name=lastname if lastname else "",
            user__email=email,
            user__username=email,
            journals=subscription.journal,
            journal_management_subscription=subscription,
        ).exists()

    def test_unlimited_plans_are_never_full(self):
        plan = JournalManagementPlanFactory(is_unlimited=True)
        subscription = JournalManagementSubscriptionFactory.create(plan=plan)
        assert subscription.slots_left == 10 ** 5
        assert not subscription.is_full

    def test_can_count_subscriptions_to_know_if_its_full(self):
        plan = JournalManagementPlanFactory.create(max_accounts=5)
        subscription = JournalManagementSubscriptionFactory.create(plan=plan)

        JournalAccessSubscriptionFactory.create_batch(
            4, journal_management_subscription=subscription
        )
        assert not subscription.is_full
        JournalAccessSubscriptionFactory.create(journal_management_subscription=subscription)
        assert subscription.is_full

    def test_can_count_pending_subscriptions_to_know_if_its_full(self):
        journal = JournalFactory()

        plan = JournalManagementPlanFactory.create(max_accounts=5)
        subscription = JournalManagementSubscriptionFactory.create(journal=journal, plan=plan)

        AccountActionTokenFactory.create_batch(4, content_object=subscription)

        assert not subscription.is_full
        AccountActionTokenFactory.create_batch(4, content_object=subscription)
        assert subscription.is_full

    def test_can_count_subscriptions_and_pending_subscriptions_to_know_if_its_full(self):
        journal = JournalFactory()

        plan = JournalManagementPlanFactory.create(max_accounts=5)
        subscription = JournalManagementSubscriptionFactory.create(journal=journal, plan=plan)

        AccountActionTokenFactory.create_batch(4, content_object=subscription)

        assert not subscription.is_full
        JournalAccessSubscriptionFactory.create_batch(
            4, journal_management_subscription=subscription
        )
        assert subscription.is_full
