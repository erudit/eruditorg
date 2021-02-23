# -*- coding: utf-8 -*-

from django import forms

from core.subscription.models import InstitutionIPAddressRange


class InstitutionIPAddressRangeForm(forms.ModelForm):
    class Meta:
        model = InstitutionIPAddressRange
        fields = [
            "ip_start",
            "ip_end",
        ]

    def __init__(self, *args, **kwargs):
        self.subscription = kwargs.pop("subscription")
        super(InstitutionIPAddressRangeForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(InstitutionIPAddressRangeForm, self).save(commit=False)
        instance.subscription = self.subscription

        if commit:
            instance.save()

        return instance
