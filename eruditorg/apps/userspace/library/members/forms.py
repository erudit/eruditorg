# -*- coding: utf-8 -*-

from account_actions.models import AccountActionToken
from django import forms
from django.utils.translation import gettext_lazy as _

from core.journal.account_actions import OrganisationMembershipAction


class OrganisationMembershipTokenCreateForm(forms.ModelForm):
    class Meta:
        model = AccountActionToken
        fields = [
            "email",
            "first_name",
            "last_name",
        ]

    def __init__(self, *args, **kwargs):
        self.organisation = kwargs.pop("organisation")
        super(OrganisationMembershipTokenCreateForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get("email")

        # First checks if a pending membership token already exists with this email address
        token_already_exists = (
            AccountActionToken.pending_objects.get_for_object(self.organisation)
            .filter(action=OrganisationMembershipAction.name, email=email)
            .exists()
        )
        if token_already_exists:
            self.add_error("email", _("Une proposition existe déjà pour cette adresse courriel"))

        # Then checks if the considered user is already a member of the organisation
        if self.organisation.members.filter(email=email).exists():
            self.add_error(
                "email",
                _("Un utilisateur avec cette adresse courriel est déjà membre de l'organisation"),
            )

        return email

    def save(self, commit=True):
        instance = super(OrganisationMembershipTokenCreateForm, self).save(commit=False)
        instance.action = OrganisationMembershipAction.name
        instance.content_object = self.organisation

        if commit:
            instance.save()

        return instance
