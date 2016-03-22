# -*- coding: utf-8 -*-

from django import forms

from core.subscription.models import JournalAccessSubscription


class JournalAccessSubscriptionForm(forms.ModelForm):
    class Meta:
        model = JournalAccessSubscription
        fields = []
