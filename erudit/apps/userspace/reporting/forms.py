# -*- coding: utf-8 -*-

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.utils.translation import ugettext_lazy as _


class ReportingFilterForm(forms.Form):
    journal = forms.CharField(max_length=255, label=_('Code revue'), required=False)
    author = forms.CharField(max_length=255, label=_('Auteur'), required=False)

    def __init__(self, *args, **kwargs):
        super(ReportingFilterForm, self).__init__(*args, **kwargs)

        # TODO: remove crispy-forms
        self.helper = FormHelper()
        self.helper.form_method = 'GET'

        self.helper.add_input(Submit('submit', _('Filtrer')))
