# -*- coding: utf-8 -*-

from django import forms

from core.subscription.models import JournalAccessSubscription


class JournalAccessSubscriptionCreateForm(forms.ModelForm):
    class Meta:
        model = JournalAccessSubscription
        fields = []


class JournalAccessSubscriptionUpdateForm(forms.ModelForm):
    class Meta:
        model = JournalAccessSubscription
        fields = []
