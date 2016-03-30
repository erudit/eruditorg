# -*- coding: utf-8 -*-

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.utils.translation import ugettext_lazy as _

from core.account_actions.models import AccountActionToken
from core.subscription.account_actions import IndividualSubscriptionAction
from core.subscription.models import JournalAccessSubscription


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

    def clean_email(self):
        email = self.cleaned_data.get('email')

        # First checks if a pending subscription token already exists with this email address
        token_already_exists = AccountActionToken.pending_objects.get_for_object(self.journal) \
            .filter(action=IndividualSubscriptionAction.name, email=email).exists()
        if token_already_exists:
            self.add_error(
                'email',
                _("Une proposition d'abonnement pour cette adresse e-mail existe déjà"))

        # Then checks if a subscription already exists for a user with this email address
        subscription_already_exists = JournalAccessSubscription.objects.filter(
            journal=self.journal, user__email=email).exists()
        if subscription_already_exists:
            self.add_error(
                'email',
                _("Une abonnement utilisant cette adresse e-mail existe déjà"))

        return email

    def save(self, commit=True):
        instance = super(JournalAccessSubscriptionCreateForm, self).save(commit=False)
        instance.action = IndividualSubscriptionAction.name
        instance.content_object = self.journal

        if commit:
            instance.save()

        return instance
