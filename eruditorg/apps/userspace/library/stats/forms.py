import datetime as dt
import typing
from django import forms
from django.utils.translation import (
    ugettext_lazy as _,
)

FORMAT_CHOICES = [
    ('csv', 'CSV'),
    ('xml', 'XML'),
    ('html', 'HTML'),
]

MONTH_CHOICES = [('', '')] + [
    (str(month), _(dt.date(2000, month, 1).strftime("%B"))) for month in range(1, 13)
]


class CounterReportForm(forms.Form):
    month_start = forms.TypedChoiceField(choices=MONTH_CHOICES, required=False, coerce=int)
    month_end = forms.TypedChoiceField(choices=MONTH_CHOICES, required=False, coerce=int)

    def __init__(self, form_info, end_year, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_info = form_info
        self.release = form_info.counter_release

        year_choices = [('', '')] + [
            (str(y), str(y)) for y in range(end_year, 2008, -1)
        ]

        year_period_choices = [('', '')] + [
            (str(y), str(y)) for y in range(end_year, 2010, -1)
        ]

        self.fields['year'] = forms.TypedChoiceField(choices=year_choices, required=False,
                                                     coerce=int)
        self.fields['year_start'] = forms.TypedChoiceField(choices=year_period_choices,
                                                           required=False, coerce=int)
        self.fields['year_end'] = forms.TypedChoiceField(choices=year_period_choices,
                                                         required=False, coerce=int)

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

    def get_report_period(self) -> typing.Tuple[dt.date, dt.date]:
        # TODO: incohérence: la date de fin est-elle incluse dans le rapport ou non ?
        #    dans tous les cas soit l'année, soit le dernier mois sont faux.
        cleaned_data = self.cleaned_data
        year = cleaned_data.get('year', None)
        if year:
            return dt.date(year, 1, 1), dt.date(year, 12, 31)

        month_start = cleaned_data['month_start']
        month_end = cleaned_data['month_end']
        year_start = cleaned_data['year_start']
        year_end = cleaned_data['year_end']

        return dt.date(year_start, month_start, 1), dt.date(year_end, month_end, 1)


class CounterR4Form(CounterReportForm):
    format = forms.ChoiceField(choices=FORMAT_CHOICES, required=False)


class CounterJR1Form(CounterR4Form):
    prefix = "counter_jr1"
    report_type = forms.CharField(
        initial="counter-jr1", widget=forms.HiddenInput(), required=False
    )


class CounterJR1GOAForm(CounterR4Form):
    prefix = "counter_jr1_goa"
    report_type = forms.CharField(
        initial="counter-jr1-goa", widget=forms.HiddenInput()
    )


class CounterR5TRJ1Form(CounterReportForm):
    prefix = "counter_r5_trj1"


class CounterR5TRJ3Form(CounterReportForm):
    prefix = "counter_r5_trj3"


class CounterR5IRA1Form(CounterReportForm):
    prefix = "counter_r5_ira1"


class StatsFormInfo(typing.NamedTuple):
    code: str
    form_class: typing.Type[CounterReportForm]
    tab_label: str
    title: str
    description: str
    counter_release: str

    @property
    def submit_name(self):
        return 'submit-{}'.format(self.code)


STATS_FORMS_INFO = [
    StatsFormInfo(
        code='counter-jr1',
        form_class=CounterJR1Form,
        tab_label=_('JR1'),
        title=_('Journal Report 1'),
        description=_("Nombre de requêtes réussies d’articles en texte intégral par mois et par "
                      "revue"),
        counter_release='R4',
    ),
    StatsFormInfo(
        code='counter-jr1-goa',
        form_class=CounterJR1GOAForm,
        tab_label=_('JR1_GOA'),
        title=_('Journal Report 1 GOA'),
        description=_("Nombre de requêtes réussies d’articles en libre accès en texte intégral par "
                      "mois et par revue"),
        counter_release='R4',
    ),
    StatsFormInfo(
        code='counter-r5-trj1',
        form_class=CounterR5TRJ1Form,
        tab_label=_('TR_J1'),
        title=_('Journal Requests (Excluding OA_Gold)'),
        description=_("Nombre de requêtes réussies d’articles en accès restreint en texte intégral "
                      "par mois et par revue"),
        counter_release='R5',
    ),
    StatsFormInfo(
        code='counter-r5-trj3',
        form_class=CounterR5TRJ3Form,
        tab_label=_('TR_J3'),
        title=_('Journal Usage by Access Type'),
        description=_("Nombre de requêtes réussies d’articles en texte intégral "
                      "par mois, par revue et par type d'accès"),
        counter_release='R5',
    ),
    StatsFormInfo(
        code='counter-r5-ira1',
        form_class=CounterR5TRJ3Form,
        tab_label=_('IR_A1'),
        title=_('Journal Article Requests'),
        description=_("Nombre de requêtes réussies d’articles en texte intégral "
                      "par mois et par article"),
        counter_release='R5',
    ),
]
