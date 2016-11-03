# -*- coding: utf-8 -*-

import datetime as dt

from django import forms
from django.utils.translation import ugettext_lazy as _


class ReportingFilterForm(forms.Form):
    author = forms.CharField(max_length=255, label=_('Auteur'), required=False)
    journal = forms.CharField(max_length=255, label=_('Code revue'), required=False)
    type = forms.MultipleChoiceField(
        label=_('Type'), required=False,
        choices=[
            ('Article', _('Article')),
            ('Culturel', _('Culturel')),
            ('Actes', _('Actes')),
            ('Thèses', _('Thèses')),
            ('Livres', _('Livres')),
            ('Dépôt', _('Dépôt')),
        ])
    year = forms.MultipleChoiceField(label=_('Année'), required=False,)
    collection = forms.MultipleChoiceField(
        label=_('Type'), required=False,
        choices=[
            ('Érudit', _('Érudit')),
            ('UNB', _('UNB')),
            ('Persée', _('Persée')),
        ])

    def __init__(self, *args, **kwargs):
        super(ReportingFilterForm, self).__init__(*args, **kwargs)
        now_dt = dt.datetime.now()

        # Update some fields
        self.fields['year'].choices = [(y, y) for y in range(now_dt.year - 50, now_dt.year)]
