# -*- coding: utf-8 -*-

from itertools import groupby

from django import forms
from django.utils.translation import ugettext_lazy as _
from erudit.models import Journal


class JournalListFilterForm(forms.Form):
    open_access = forms.BooleanField(label=_('Libre accès'), required=False)
    types = forms.MultipleChoiceField(
        label=_('Par type'), required=False, help_text='TODO')
    collections = forms.MultipleChoiceField(
        label=_('Par fonds'), required=False, help_text='TODO')

    def __init__(self, *args, **kwargs):
        super(JournalListFilterForm, self).__init__(*args, **kwargs)

        journals = Journal.objects.select_related('collection', 'type').all()
        journal_types = sorted(
            set([t[0] for t in groupby(journals, key=lambda j: j.type) if t[0]]),
            key=lambda t: t.name)
        journal_collections = sorted(
            set([c[0] for c in groupby(journals, key=lambda j: j.collection) if c[0]]),
            key=lambda c: c.name)

        # Updates some fields
        self.fields['types'].choices = [(t.code, t.name) for t in journal_types]
        self.fields['collections'].choices = [(c.code, c.name) for c in journal_collections]
