# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import gettext_lazy as _

from erudit.models import Organisation


class SubscriptionInformationForm(forms.Form):
    badge = Organisation._meta.get_field('badge').formfield()

    def __init__(self, *args, **kwargs):
        self.organisation = kwargs.pop('organisation')
        super(SubscriptionInformationForm, self).__init__(*args, **kwargs)

        # Updates some fields
        self.fields['badge'].initial = self.organisation.badge
        self.fields['badge'].help_text = _(
            'Le badge ne doit pas excéder 140x140 pixels et sera automatiquement redimensionné '
            'dans le cas contraire.')

    def save(self, commit=True):
        badge_field = Organisation._meta.get_field('badge')

        if commit:
            badge_field.save_form_data(self.organisation, self.cleaned_data['badge'])
            self.organisation.save()

        return self.organisation
