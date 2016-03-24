# -*- coding: utf-8 -*-

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.utils.translation import ugettext_lazy as _

from core.account_actions.models import AccountActionToken
from core.subscription.account_actions import IndividualSubscriptionAction


class JournalAccessSubscriptionCreateForm(forms.ModelForm):
    class Meta:
        model = AccountActionToken
        fields = ['email', 'first_name', 'last_name', ]

    def __init__(self, *args, **kwargs):
        self.journal = kwargs.pop('journal')
        super(JournalAccessSubscriptionCreateForm, self).__init__(*args, **kwargs)

        # TODO: remove crispy-forms
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', _('Valider')))

    def save(self, commit=True):
        instance = super(JournalAccessSubscriptionCreateForm, self).save(commit=False)
        instance.action = IndividualSubscriptionAction.name
        instance.content_object = self.journal

        if commit:
            instance.save()

        return instance
