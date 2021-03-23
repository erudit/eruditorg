import datetime

from apps.userspace.library.stats.forms import (
    CounterJR1Form,
    DatesRange,
)

DATES_RANGE_2009_2019 = DatesRange(datetime.date(2009, 3, 1), datetime.date(2019, 6, 30))


class TestLibraryDashboardCounterForm:
    def test_counter_form_can_limit_year_to_last_year_of_subscription(self):
        """The last selectable year should be the end year passed to the form. """
        form = CounterJR1Form(DatesRange(datetime.date(2009, 3, 1), datetime.date(2019, 7, 1)))
        years = [int(choice[0]) for choice in form.fields["year"].choices]
        assert max(years) == 2019
        assert min(years) == 2009

    def test_counter_form_supports_year_and_format(self):
        """Form should be valid if passed a year and a format. """
        prefix = CounterJR1Form.prefix
        data = {
            f"{prefix}-period_type": "annual",
            f"{prefix}-report_type": "annual",
            f"{prefix}-year": 2017,
            f"{prefix}-month_start": 1,
            f"{prefix}-month_end": 12,
            f"{prefix}-year_start": 2017,
            f"{prefix}-year_end": 2018,
            f"{prefix}-format": "csv",
        }
        form = CounterJR1Form(DATES_RANGE_2009_2019, data=data)
        assert form.is_valid(), form.errors

    def test_counter_form_supports_months_period(self):
        """Form should be valid if start and end months/years are selected. """
        prefix = CounterJR1Form.prefix
        data = {
            f"{prefix}-period_type": "monthly",
            f"{prefix}-year": 2017,
            f"{prefix}-month_start": 1,
            f"{prefix}-year_start": 2017,
            f"{prefix}-month_end": 12,
            f"{prefix}-year_end": 2018,
            f"{prefix}-format": "csv",
        }

        form = CounterJR1Form(DATES_RANGE_2009_2019, data=data)
        assert form.is_valid(), form.errors

    def test_counter_form_needs_end_date_higher_than_start_date(self):
        """Form shouldn't validate if end month is earlier than start month. """
        prefix = CounterJR1Form.prefix
        data = {
            f"{prefix}-period_type": "monthly",
            f"{prefix}-year": 2017,
            f"{prefix}-month_start": 1,
            f"{prefix}-year_start": 2018,
            f"{prefix}-month_end": 12,
            f"{prefix}-year_end": 2017,
            f"{prefix}-format": "csv",
        }

        form = CounterJR1Form(DATES_RANGE_2009_2019, data=data)
        assert not form.is_valid()
        assert form.has_error("__all__", code="end_before_start")

    def test_can_return_year_period(self):
        """Form should be valid and return an inclusive all-year range if a year was selected. """
        prefix = CounterJR1Form.prefix
        data = {
            f"{prefix}-period_type": "annual",
            f"{prefix}-year": 2017,
            f"{prefix}-month_start": 1,
            f"{prefix}-year_start": 2018,
            f"{prefix}-month_end": 12,
            f"{prefix}-year_end": 2017,
            f"{prefix}-format": "csv",
        }

        form = CounterJR1Form(DATES_RANGE_2009_2019, data=data)
        assert form.is_valid(), form.errors
        assert form.get_report_period() == (
            datetime.date(2017, 1, 1),
            datetime.date(2017, 12, 31),
        )

    def test_can_return_year_period_when_selected_year_incomplete_first_year(self):
        """Form should be valid and the report period should correspond only to that part of the
        year that's available when the selected year is the first available year.

        """

        prefix = CounterJR1Form.prefix
        data = {
            f"{prefix}-period_type": "annual",
            f"{prefix}-year": 2009,
            f"{prefix}-month_start": 1,
            f"{prefix}-year_start": 2018,
            f"{prefix}-month_end": 12,
            f"{prefix}-year_end": 2017,
            f"{prefix}-format": "csv",
        }

        form = CounterJR1Form(DATES_RANGE_2009_2019, data=data)
        assert form.is_valid(), form.errors
        assert form.get_report_period() == (
            datetime.date(2009, 3, 1),
            datetime.date(2009, 12, 31),
        )

    def test_can_return_year_period_when_selected_year_incomplete_last_year(self):
        """Form should be valid and the report period should correspond only to that part of the
        year that's available when the selected year is the last available year.

        """

        prefix = CounterJR1Form.prefix
        data = {
            f"{prefix}-period_type": "annual",
            f"{prefix}-year": 2019,
            f"{prefix}-month_start": 1,
            f"{prefix}-year_start": 2018,
            f"{prefix}-month_end": 12,
            f"{prefix}-year_end": 2017,
            f"{prefix}-format": "csv",
        }

        form = CounterJR1Form(DATES_RANGE_2009_2019, data=data)
        assert form.is_valid(), form.errors
        assert form.get_report_period() == (
            datetime.date(2019, 1, 1),
            datetime.date(2019, 6, 30),
        )

    def test_can_return_months_period(self):
        """Form should be valid when start and end months are selected, and it should return a range
        ending on the last day of end month.

        """

        prefix = CounterJR1Form.prefix
        data = {
            f"{prefix}-period_type": "monthly",
            f"{prefix}-year": 2019,
            f"{prefix}-month_start": 1,
            f"{prefix}-year_start": 2017,
            f"{prefix}-month_end": 12,
            f"{prefix}-year_end": 2018,
            f"{prefix}-format": "csv",
        }

        form = CounterJR1Form(DATES_RANGE_2009_2019, data=data)
        assert form.is_valid(), form.errors
        assert form.get_report_period() == (
            datetime.date(2017, 1, 1),
            datetime.date(2018, 12, 31),
        )
