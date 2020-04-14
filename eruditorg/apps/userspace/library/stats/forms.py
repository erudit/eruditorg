import datetime as dt
from django import forms
from django.utils.translation import gettext_lazy as _
from apps.userspace.library.shortcuts import get_last_year_of_subscription

current_year = dt.datetime.now().year

FORMAT_CHOICES = [
    ('csv', 'CSV'),
    ('xml', 'XML'),
    ('html', 'HTML'),
]

MONTH_CHOICES = [
    ('', ''),
    (1, _('janvier')),
    (2, _('février')),
    (3, _('mars')),
    (4, _('avril')),
    (5, _('mai')),
    (6, _('juin')),
    (7, _('juillet')),
    (8, _('août')),
    (9, _('septembre')),
    (10, _('octobre')),
    (11, _('novembre')),
    (12, _('décembre')),
]


class CounterReport(forms.Form):
    def __init__(self, organisation=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        end_year = get_last_year_of_subscription(organisation)
        if end_year is None:
            end_year = current_year
        else:
            end_year = end_year if end_year <= current_year else current_year

        year_choices = [('', '')] + [
            (y, y) for y in range(end_year, end_year - (end_year - 2008), -1)
        ]

        year_period_choices = [('', '')] + [
            (y, y) for y in range(end_year, end_year - (end_year - 2010), -1)
        ]

        self.fields['year'] = forms.ChoiceField(choices=year_choices, required=False)
        self.fields['year_start'] = forms.ChoiceField(choices=year_period_choices, required=False)
        self.fields['year_end'] = forms.ChoiceField(choices=year_period_choices, required=False)
        self.fields['month_start'] = forms.ChoiceField(choices=MONTH_CHOICES, required=False)
        self.fields['month_end'] = forms.ChoiceField(choices=MONTH_CHOICES, required=False)
        self.fields['format'] = forms.ChoiceField(choices=FORMAT_CHOICES, required=False)

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
