# -*- coding: utf-8 -*-

import datetime as dt

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.utils.translation import ugettext_lazy as _


class ReportingFilterForm(forms.Form):
    journal = forms.CharField(max_length=255, label=_('Code revue'), required=False)
    author = forms.CharField(max_length=255, label=_('Auteur'), required=False)
    year = forms.ChoiceField(label=_('Année'), required=False,)

    def __init__(self, *args, **kwargs):
        super(ReportingFilterForm, self).__init__(*args, **kwargs)
        now_dt = dt.datetime.now()

        # Update some fields
        self.fields['year'].choices = [(y, y) for y in range(now_dt.year-50, now_dt.year)]

        # TODO: remove crispy-forms
        self.helper = FormHelper()
        self.helper.form_method = 'GET'

        self.helper.add_input(Submit('submit', _('Filtrer')))
