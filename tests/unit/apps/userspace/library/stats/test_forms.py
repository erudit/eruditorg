import pytest
from datetime import datetime, timedelta
from apps.userspace.library.stats.forms import CounterJR1GOAForm, CounterJR1Form, CounterReport

from erudit.test.factories import OrganisationFactory
from core.subscription.test.factories import JournalAccessSubscriptionFactory, JournalAccessSubscriptionPeriodFactory


@pytest.mark.django_db
class TestLibraryDashboardCounterForm:

    def test_can_create_counter_forms_when_no_subscription(self):
        organisation = OrganisationFactory()
        CounterJR1Form(organisation=organisation)
        CounterJR1GOAForm(organisation=organisation)

    def test_can_create_counter_form_when_organisation_has_subscription(self):
        organisation = OrganisationFactory()
        subscription = JournalAccessSubscriptionFactory(post__valid=True, organisation=organisation)
        CounterJR1Form(organisation=organisation)
        CounterJR1GOAForm(organisation=organisation)

    def test_counter_form_can_limit_year_to_last_year_of_subscription(self):
        organisation = OrganisationFactory()
        subscription = JournalAccessSubscriptionFactory(organisation=organisation)
        JournalAccessSubscriptionPeriodFactory.create(
            subscription=subscription,
            start=datetime(day=1, month=1, year=2008),
            end=datetime(day=31, month=12, year=2009),
        )
        form = CounterJR1Form(organisation=organisation)
        years = [choice[0] for choice in form.fields['year'].choices if isinstance(choice[0], int)]
        assert max(years) == 2009

    def test_counter_form_can_limit_year_to_current_year(self):
        organisation = OrganisationFactory()
        subscription = JournalAccessSubscriptionFactory(organisation=organisation)
        now = datetime.now()
        JournalAccessSubscriptionPeriodFactory.create(
            subscription=subscription,
            start=datetime(day=1, month=1, year=2008),
            end=now + timedelta(weeks=52)
        )
        form = CounterJR1Form(organisation=organisation)
        years = [choice[0] for choice in form.fields['year'].choices if isinstance(choice[0], int)]
        assert max(years) == now.year

    def test_counter_form_supports_year_and_format(self):
        organisation = OrganisationFactory()
        prefix = CounterJR1Form.prefix
        data = {'{}-year'.format(prefix): 2017, '{}-format'.format(prefix): 'csv'}
        form = CounterJR1Form(organisation=organisation, data=data)
        assert form.is_valid()

    def test_counter_form_supports_year_period(self):
        organisation = OrganisationFactory()
        prefix = CounterJR1Form.prefix
        data = {
            '{}-month_start'.format(prefix): 1,
            '{}-month_end'.format(prefix): 12,
            '{}-year_start'.format(prefix): 2017,
            '{}-year_end'.format(prefix): 2018,
            '{}-format'.format(prefix): 'csv'
        }

        form = CounterJR1Form(organisation=organisation, data=data)
        assert form.is_valid()

    def test_counter_form_needs_end_date_higher_than_start_date(self):
        organisation = OrganisationFactory()
        prefix = CounterJR1Form.prefix
        data = {
            '{}-month_start'.format(prefix): 1,
            '{}-month_end'.format(prefix): 12,
            '{}-year_start'.format(prefix): 2018,
            '{}-year_end'.format(prefix): 2017,
            '{}-format'.format(prefix): 'csv'
        }

        form = CounterJR1Form(organisation=organisation, data=data)
        assert not form.is_valid()

