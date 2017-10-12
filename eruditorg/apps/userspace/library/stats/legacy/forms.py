import datetime as dt
from django import forms
from django.utils.translation import gettext as _

current_year = dt.datetime.now().year

YEAR_CHOICES = [('', '')] + [
    (y, y) for y in range(current_year, current_year - (current_year - 2008), -1)
]

YEAR_PERIOD_CHOICES = [('', '')] + [
    (y, y) for y in range(current_year, current_year - (current_year - 2010), -1)
]

MONTH_CHOICES = [('', '')] + [
    (month, _(dt.date(current_year, month, 1).strftime("%B"))) for month in range(1, 13)
]

FORMAT_CHOICES = [
    ('csv', 'CSV'),
    ('xml', 'XML'),
    ('html', 'HTML'),
]


class CounterReport(forms.Form):

    year = forms.ChoiceField(
        label=_("Année"), widget=forms.Select(), choices=YEAR_CHOICES, required=False
    )

    month_start = forms.ChoiceField(
        label=_("Mois"), widget=forms.Select(), choices=MONTH_CHOICES, required=False
    )

    year_start = forms.ChoiceField(
        label=_("Année"), widget=forms.Select(), choices=YEAR_PERIOD_CHOICES, required=False
    )

    month_end = forms.ChoiceField(
        label=_("Mois"), widget=forms.Select(), choices=MONTH_CHOICES, required=False
    )

    year_end = forms.ChoiceField(
        label=_("Année"), widget=forms.Select(), choices=YEAR_PERIOD_CHOICES, required=False
    )

    format = forms.ChoiceField(
        label=_("Format"), widget=forms.Select(), choices=FORMAT_CHOICES, required=True
    )

    def clean(self):
        cleaned_data = super().clean()

        year = cleaned_data.get('year', None)
        month_start = cleaned_data.get('month_start', None)
        month_end = cleaned_data.get('month_end', None)
        year_start = cleaned_data.get('year_start', None)
        year_end = cleaned_data.get('year_end', None)

        if not year and not all([month_start, month_end, year_start, year_end]):
            self.add_error('year', _("Vous devez spécifier l'année ou la période"))

        if all([month_start, month_end, year_start, year_end]):
            dstart = dt.date(int(year_start), int(month_start), 1)
            dend = dt.date(int(year_end), int(month_end), 1)

            if dstart >= dend:
                self.add_error(
                    'year_start', _("La date de début doit être inférieure à la date de fin")
                )

            if dend - dt.timedelta(weeks=104) > dstart:
                self.add_error('year_start', _("La période doit être de deux ans maximum"))

        return cleaned_data


class CounterJR1Form(CounterReport):
    prefix = "counter_jr1"
    report_type = forms.CharField(
        initial="counter-jr1", widget=forms.HiddenInput(), required=False
    )


class CounterJR1GOAForm(CounterReport):
    prefix = "counter_jr1_goa"
    report_type = forms.CharField(
        initial="counter-jr1-goa", widget=forms.HiddenInput()
    )
