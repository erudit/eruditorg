# -*- coding: utf-8 -*-

from ckeditor.widgets import CKEditorWidget
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.forms.models import fields_for_model
from django.utils.translation import ugettext_lazy as _

from .models import JournalInformation


class JournalInformationForm(forms.ModelForm):
    i18n_field_bases = [
        'about', 'editorial_policy', 'subscriptions',
        'team', 'contact', 'partners',
    ]

    class Meta:
        model = JournalInformation
        fields = []

    def __init__(self, *args, **kwargs):
        self.language_code = kwargs.pop('language_code')
        super(JournalInformationForm, self).__init__(*args, **kwargs)

        # Fetches proper labels for for translatable fields: this is necessary
        # in order to remove language indications from labels (eg. "Team [en]")
        i18n_fields_label = {
            self.get_i18n_field_name(fname): self._meta.model._meta.get_field(fname).verbose_name
            for fname in self.i18n_field_bases}

        # All translatable fields are TextField and will use CKEditor
        i18n_field_widgets = {fname: CKEditorWidget() for fname in self.i18n_field_names}

        # Inserts the translatable fields into the form fields.
        self.fields.update(
            fields_for_model(self.Meta.model, fields=self.i18n_field_names,
                             labels=i18n_fields_label, widgets=i18n_field_widgets))

        # TODO: remove crispy-forms
        self.helper = FormHelper()
        self.helper.form_tag = False

        self.helper.add_input(Submit('submit', _('Enregistrer')))

    @property
    def i18n_field_names(self):
        return [self.get_i18n_field_name(fname) for fname in self.i18n_field_bases]

    def get_i18n_field_name(self, fname):
        return fname + '_' + self.language_code

    def save(self, commit=True):
        obj = super(JournalInformationForm, self).save(commit)
        # Forces the save of dynamic i18n fields
        for fname in self.i18n_field_names:
            setattr(obj, fname, self.cleaned_data[fname])

        if commit:
            obj.save()
        return obj
