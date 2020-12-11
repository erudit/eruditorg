import calendar
import datetime as dt
import typing
from django import forms
from django.utils.translation import gettext_lazy as _

FORMAT_CHOICES = [
    ("csv", "CSV"),
    ("xml", "XML"),
    ("html", "HTML"),
]

MONTH_CHOICES = [
    (1, _("janvier")),
    (2, _("février")),
    (3, _("mars")),
    (4, _("avril")),
    (5, _("mai")),
    (6, _("juin")),
    (7, _("juillet")),
    (8, _("août")),
    (9, _("septembre")),
    (10, _("octobre")),
    (11, _("novembre")),
    (12, _("décembre")),
]


class DatesRange(typing.NamedTuple):
    first_day: dt.date
    last_day: dt.date

    @property
    def first_year(self):
        return self.first_day.year

    @property
    def first_month(self):
        return self.first_day.month

    @property
    def last_year(self):
        return self.last_day.year

    @property
    def last_month(self):
        return self.last_day.month


def get_month_period(cleaned_data: dict) -> DatesRange:
    """Compute first and last date for a months-spanning period stored in cleaned_data, starting at
    the first day of the start month to the last day of the end month. This function expects
    cleaned_data to contain the expected fields with valid data in them.

    """

    # those fields are required and coerced to int so the cast is safe
    month_start = typing.cast(int, cleaned_data["month_start"])
    month_end = typing.cast(int, cleaned_data["month_end"])
    year_start = typing.cast(int, cleaned_data["year_start"])
    year_end = typing.cast(int, cleaned_data["year_end"])
    last_day_of_end_month = calendar.monthrange(year_end, month_end)[1]
    end_date = dt.date(year_end, month_end, last_day_of_end_month)
    return DatesRange(dt.date(year_start, month_start, 1), end_date)


class CounterReportForm(forms.Form):
    code: str
    tab_label: str
    title: str
    description: str
    counter_release: str

    period_type = forms.ChoiceField(
        choices=[
            ("monthly", _("Période mensuelle")),
            ("annual", _("Période annuelle")),
        ],
        initial="monthly",
        widget=forms.RadioSelect,
        required=True,
    )
    month_start = forms.TypedChoiceField(choices=MONTH_CHOICES, required=True, coerce=int)
    month_end = forms.TypedChoiceField(choices=MONTH_CHOICES, required=True, coerce=int)
    year_start = forms.TypedChoiceField(choices=(), required=True, coerce=int)
    year_end = forms.TypedChoiceField(choices=(), required=True, coerce=int)
    year = forms.TypedChoiceField(choices=(), required=True, coerce=int)

    def __init__(self, available_range: DatesRange, *args, **kwargs):
        """Base form for both Counter R4 and R5 reports.

        To simplify validation all fields are required, and all have initial values set in __init__
        according to the available range.

        :param available_range: The range of dates for which data is available (inclusive)
        """

        self.available_range = available_range
        end_year = available_range.last_year
        last_month = available_range.last_month
        # the default range for reports is the latest available month or year
        initial = kwargs["initial"] = kwargs.get("initial", {})
        initial.update(
            {
                "year": end_year,
                "year_start": end_year,
                "month_start": last_month,
                "year_end": end_year,
                "month_end": last_month,
            }
        )

        super().__init__(*args, **kwargs)

        first_year = available_range.first_year
        available_years = list(range(end_year, first_year - 1, -1))
        year_period_choices = [(str(y), str(y)) for y in available_years]
        self.fields["year_start"].choices = year_period_choices
        self.fields["year_end"].choices = year_period_choices
        self.fields["year"].choices = year_period_choices

    def clean(self):
        cleaned_data = super().clean()
        if not self.errors and cleaned_data["period_type"] == "monthly":
            start_date, end_date = get_month_period(cleaned_data)
            if start_date >= end_date:
                raise forms.ValidationError(
                    _("La date de début doit être inférieure à la date de fin"),
                    code="end_before_start",
                )

            if end_date - start_date > dt.timedelta(weeks=105):
                raise forms.ValidationError(
                    _("La période doit être de deux ans maximum"), code="too_long"
                )

        return cleaned_data

    def get_report_period(self) -> DatesRange:
        """Compute the report period as begin and end dates from what was entered in the form. It's
        expected that the form data has been cleaned and validated before calling this method.

        The period selected can be a whole year or a range of months. In any case, everything is
        inclusive: first month and last month are included in the range, and the dates returned
        are also inclusive. That means that in the case of a month range, the end date is the last
        day of the selected end month (as required by the R5 spec and R5 library).

        """

        cleaned_data = self.cleaned_data
        if cleaned_data["period_type"] == "annual":
            year = cleaned_data["year"]
            if year == self.available_range.last_year:
                return get_month_period(
                    {
                        "year_start": year,
                        "month_start": 1,
                        "year_end": year,
                        "month_end": self.available_range.last_month,
                    }
                )
            elif year == self.available_range.first_year:
                return get_month_period(
                    {
                        "year_start": year,
                        "month_start": self.available_range.first_month,
                        "year_end": year,
                        "month_end": 12,
                    }
                )
            else:
                return DatesRange(dt.date(year, 1, 1), dt.date(year, 12, 31))

        return get_month_period(cleaned_data)

    @classmethod
    def submit_name(cls):
        return f"submit-{cls.code}"


class CounterR4Form(CounterReportForm):
    format = forms.ChoiceField(choices=FORMAT_CHOICES, required=True)


class CounterJR1Form(CounterR4Form):
    code = "counter-jr1"
    tab_label = _("JR1")
    title = _("Journal Report 1")
    description = _(
        "Nombre de requêtes réussies d’articles en texte intégral par mois et par revue"
    )
    counter_release = "R4"
    prefix = "counter_jr1"
    is_gold_open_access = False


class CounterJR1GOAForm(CounterR4Form):
    code = "counter-jr1-goa"
    tab_label = _("JR1_GOA")
    title = _("Journal Report 1 GOA")
    description = _(
        "Nombre de requêtes réussies d’articles en libre accès en texte intégral par "
        "mois et par revue"
    )
    counter_release = "R4"
    prefix = "counter_jr1_goa"
    is_gold_open_access = True


class CounterR5Form(CounterReportForm):
    counter_release = "R5"


class CounterR5TRJ1Form(CounterR5Form):
    code = "counter-r5-trj1"
    tab_label = _("TR_J1")
    title = _("Journal Requests (Excluding OA_Gold)")
    description = _(
        "Nombre de requêtes réussies d’articles en accès restreint en texte intégral "
        "par mois et par revue"
    )
    prefix = "counter_r5_trj1"
    report_code = "TR_J1"


class CounterR5TRJ3Form(CounterR5Form):
    code = "counter-r5-trj3"
    tab_label = _("TR_J3")
    title = _("Journal Usage by Access Type")
    description = _(
        "Nombre de requêtes réussies d’articles en texte intégral "
        "par mois, par revue et par type d'accès"
    )
    prefix = "counter_r5_trj3"
    report_code = "TR_J3"


class CounterR5IRA1Form(CounterR5Form):
    code = "counter-r5-ira1"
    tab_label = _("IR_A1")
    title = _("Journal Article Requests")
    description = _(
        "Nombre de requêtes réussies d’articles en texte intégral par mois et par article"
    )
    prefix = "counter_r5_ira1"
    report_code = "IR_A1"


REPORT_FORMS = [
    CounterJR1Form,
    CounterJR1GOAForm,
    CounterR5TRJ1Form,
    CounterR5TRJ3Form,
    CounterR5IRA1Form,
]
