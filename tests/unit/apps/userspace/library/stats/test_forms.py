import datetime

from apps.userspace.library.stats.forms import (
    CounterJR1Form,
    STATS_FORMS_INFO,
)


class TestLibraryDashboardCounterForm:
    def test_counter_form_can_limit_year_to_last_year_of_subscription(self):
        form = CounterJR1Form(STATS_FORMS_INFO[0], 2019)
        years = [int(choice[0]) for choice in form.fields['year'].choices[1:]]
        assert max(years) == 2019
        assert min(years) == 2009

    def test_counter_form_supports_year_and_format(self):
        prefix = CounterJR1Form.prefix
        data = {'{}-year'.format(prefix): 2017, '{}-format'.format(prefix): 'csv'}
        form = CounterJR1Form(STATS_FORMS_INFO[0], 2019, data=data)
        assert form.is_valid()

    def test_counter_form_supports_year_period(self):
        prefix = CounterJR1Form.prefix
        data = {
            '{}-month_start'.format(prefix): 1,
            '{}-month_end'.format(prefix): 12,
            '{}-year_start'.format(prefix): 2017,
            '{}-year_end'.format(prefix): 2018,
            '{}-format'.format(prefix): 'csv'
        }

        form = CounterJR1Form(STATS_FORMS_INFO[0], 2019, data=data)
        assert form.is_valid()

    def test_counter_form_needs_end_date_higher_than_start_date(self):
        prefix = CounterJR1Form.prefix
        data = {
            '{}-month_start'.format(prefix): 1,
            '{}-month_end'.format(prefix): 12,
            '{}-year_start'.format(prefix): 2018,
            '{}-year_end'.format(prefix): 2017,
            '{}-format'.format(prefix): 'csv'
        }

        form = CounterJR1Form(STATS_FORMS_INFO[0], 2019, data=data)
        assert not form.is_valid()

    def test_can_return_year_period(self):
        prefix = CounterJR1Form.prefix
        data = {
            '{}-year'.format(prefix): 2019,
        }

        form = CounterJR1Form(STATS_FORMS_INFO[0], 2019, data=data)
        assert form.is_valid()
        assert form.get_report_period() == (datetime.date(2019, 1, 1), datetime.date(2019, 12, 31))

    def test_can_return_months_period(self):
        prefix = CounterJR1Form.prefix
        data = {
            '{}-month_start'.format(prefix): 1,
            '{}-year_start'.format(prefix): 2017,
            '{}-month_end'.format(prefix): 12,
            '{}-year_end'.format(prefix): 2018,
            '{}-format'.format(prefix): 'csv'
        }

        form = CounterJR1Form(STATS_FORMS_INFO[0], 2019, data=data)
        assert form.is_valid()
        assert form.get_report_period() == (datetime.date(2017, 1, 1), datetime.date(2018, 12, 1))
