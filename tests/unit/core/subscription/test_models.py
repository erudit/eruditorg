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
from core.subscription.test.factories import InstitutionRefererFactory
from core.subscription.test.factories import ValidJournalAccessSubscriptionPeriodFactory
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
            end=now_dt + dt.timedelta(days=8))
        JournalAccessSubscriptionPeriodFactory.create(
            subscription=subscription_2,
            start=now_dt + dt.timedelta(days=10),
            end=now_dt + dt.timedelta(days=8))
        # Run & check
        assert subscription_1.is_ongoing
        assert not subscription_2.is_ongoing

    def test_knows_it_is_an_individual_subscription(self):
        subscription = JournalAccessSubscriptionFactory(user=UserFactory(), organisation=None)
        assert subscription.get_subscription_type() == JournalAccessSubscription.TYPE_INDIVIDUAL

    def test_knows_it_is_an_institutional_subscription(self):
        subscription = JournalAccessSubscriptionFactory(organisation=OrganisationFactory(), user=None)
        assert subscription.get_subscription_type() == JournalAccessSubscription.TYPE_INSTITUTIONAL

    def test_knows_its_underlying_journals(self):
        journal = JournalFactory()
        subscription_2 = JournalAccessSubscriptionFactory.create(journal=journal)
        subscription_3 = JournalAccessSubscriptionFactory.create()
        subscription_3.journals.add(journal)
        assert list(subscription_2.get_journals()) == [journal, ]
        assert list(subscription_3.get_journals()) == [journal, ]

    def test_basket_provides_access(self):
        j1, j2, j3 = JournalFactory.create_batch(3)
        basket = AccessBasketFactory.create(journals=[j1, j2])
        sub = JournalAccessSubscriptionFactory.create(basket=basket)
        assert sub.provides_access_to(journal=j1)
        assert sub.provides_access_to(journal=j2)
        assert not sub.provides_access_to(journal=j3)


@pytest.mark.django_db
class TestUserSubscriptions:

    def test_the_first_subscription_is_the_active_subscription(self):
        from core.subscription.models import UserSubscriptions

        subs = UserSubscriptions()
        subscription = JournalAccessSubscriptionFactory()
        subs.add_subscription(subscription)
        assert subs.active_subscription == subscription


@pytest.mark.django_db
class TestInstitutionReferer:

    def test_can_find_an_institution_referer_by_netloc(self):

        valid_period = ValidJournalAccessSubscriptionPeriodFactory()
        institution_referer = InstitutionRefererFactory(
            subscription=valid_period.subscription,
            referer="https://www.erudit.org/"
        )
        assert JournalAccessSubscription.valid_objects.get_for_referer("https://www.erudit.org/") == institution_referer.subscription  # noqa
        assert JournalAccessSubscription.valid_objects.get_for_referer("http://www.erudit.org/") == institution_referer.subscription  # noqa


    def test_can_find_an_institution_referer_by_netloc_and_path(self):

        valid_period = ValidJournalAccessSubscriptionPeriodFactory()
        institution_referer = InstitutionRefererFactory(
            subscription=valid_period.subscription,
            referer="https://www.topsecurity.org/bulletproofauthenticationmechanism"
        )
        assert JournalAccessSubscription.valid_objects.get_for_referer("http://www.topsecurity.org/bulletproofauthenticationmechanism") == institution_referer.subscription  # noqa
        assert not JournalAccessSubscription.valid_objects.get_for_referer("http://www.topsecurity.org/")
        assert JournalAccessSubscription.valid_objects.get_for_referer("http://www.topsecurity.org/bulletproofauthenticationmechanism/journal123") == institution_referer.subscription  # noqa

    def test_can_find_an_institution_referer_with_netloc_port_path_and_querystring(self):
        valid_period = ValidJournalAccessSubscriptionPeriodFactory()
        institution_referer = InstitutionRefererFactory(
            subscription=valid_period.subscription,
            referer="http://externalservice.com:2049/login?url="
        )
        assert JournalAccessSubscription.valid_objects.get_for_referer("http://externalservice.com:2049/login?url='allo'") == institution_referer.subscription  # noqa
        assert JournalAccessSubscription.valid_objects.get_for_referer("https://externalservice.com:2049/login?url='allo'") == institution_referer.subscription  # noqa

    def test_can_only_find_institution_referer_when_path_fully_match(self):
        valid_period = ValidJournalAccessSubscriptionPeriodFactory()
        InstitutionRefererFactory.create(
            subscription=valid_period.subscription,
            referer="http://www.erudit.org.proxy.com/"
        )

        assert not JournalAccessSubscription.valid_objects.get_for_referer("http://www.erudit.org/")  # noqa


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
                subscription=self.subscription,
                ip_start='192.168.1.3', ip_end='192.168.1.2')
            ip_range.clean()

    def test_can_return_the_list_of_corresponding_ip_addresses(self):
        # Setup
        ip_range = InstitutionIPAddressRangeFactory.build(
            subscription=self.subscription,
            ip_start='192.168.1.3', ip_end='192.168.1.5')
        # Run
        ip_addresses = ip_range.ip_addresses
        # Check
        assert ip_addresses == [
            ipaddress.ip_address('192.168.1.3'),
            ipaddress.ip_address('192.168.1.4'),
            ipaddress.ip_address('192.168.1.5'),
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
            end=now_dt + dt.timedelta(days=8))
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
            end=now_dt + dt.timedelta(days=14))
        period = JournalAccessSubscriptionPeriodFactory.build(
            subscription=subscription,
            start=now_dt + dt.timedelta(days=10),
            end=now_dt + dt.timedelta(days=12))
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
            end=now_dt + dt.timedelta(days=11))
        period = JournalAccessSubscriptionPeriodFactory.build(
            subscription=subscription,
            start=now_dt + dt.timedelta(days=8),
            end=now_dt + dt.timedelta(days=14))
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
            end=now_dt + dt.timedelta(days=11))
        period = JournalAccessSubscriptionPeriodFactory.build(
            subscription=subscription,
            start=now_dt + dt.timedelta(days=10),
            end=now_dt + dt.timedelta(days=12))
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
            end=now_dt + dt.timedelta(days=15))
        period = JournalAccessSubscriptionPeriodFactory.build(
            subscription=subscription,
            start=now_dt + dt.timedelta(days=10),
            end=now_dt + dt.timedelta(days=12))
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

        subscription_1 = JournalManagementSubscriptionFactory.create(
            journal=journal, plan=plan)
        subscription_2 = JournalManagementSubscriptionFactory.create(
            journal=journal, plan=plan)

        JournalManagementSubscriptionPeriodFactory.create(
            subscription=subscription_1,
            start=now_dt - dt.timedelta(days=10),
            end=now_dt + dt.timedelta(days=8))
        JournalManagementSubscriptionPeriodFactory.create(
            subscription=subscription_2,
            start=now_dt + dt.timedelta(days=10),
            end=now_dt + dt.timedelta(days=8))
        # Run & check
        assert subscription_1.is_ongoing
        assert not subscription_2.is_ongoing

    def test_unlimited_plans_are_never_full(self):
        plan = JournalManagementPlanFactory(is_unlimited=True)
        subscription = JournalManagementSubscriptionFactory.create(plan=plan)
        JournalAccessSubscriptionFactory.create_batch(50, journal_management_subscription=subscription)
        assert not subscription.is_full

    def test_can_count_subscriptions_to_know_if_its_full(self):
        plan = JournalManagementPlanFactory.create(max_accounts=5)
        subscription = JournalManagementSubscriptionFactory.create(plan=plan)

        JournalAccessSubscriptionFactory.create_batch(4, journal_management_subscription=subscription)
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
        JournalAccessSubscriptionFactory.create_batch(4, journal_management_subscription=subscription)
        assert subscription.is_full
