# -*- coding: utf-8 -*-

from itertools import groupby

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify
from erudit.models import Journal, Collection


class JournalListFilterForm(forms.Form):
    open_access = forms.BooleanField(label=_('Libre accès'), required=False)
    is_new = forms.BooleanField(label=_('Nouveautés'), required=False)
    types = forms.MultipleChoiceField(
        label=_('Par type'), required=False)
    collections = forms.MultipleChoiceField(
        label=_('Par fonds'), required=False)

    def clean_collections(self):
        data = self.cleaned_data['collections']
        if not data:
            main_collections_codes = [
                c.code for c in Collection.objects.filter(is_main_collection=True)
            ]
            self['collections'].value = main_collections_codes
            return main_collections_codes
        return data

    def __init__(self, *args, **kwargs):
        super(JournalListFilterForm, self).__init__(*args, **kwargs)

        journals = Journal.objects.select_related('collection', 'type').all()
        journal_types = sorted(
            set([t[0] for t in groupby(journals, key=lambda j: j.type) if t[0]]),
            key=lambda t: t.name)
        journal_collections = sorted(
            set([c[0] for c in groupby(journals, key=lambda j: j.collection) if c[0]]),
            key=lambda c: slugify(c.name))
        # Updates some fields
        self.fields['types'].choices = [(t.code, t.name) for t in journal_types]
        self.fields['collections'].choices = [(c.code, c.name) for c in journal_collections]
