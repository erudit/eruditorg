from account_actions.models import AccountActionToken
from django import forms
from django.utils.translation import gettext as _

from core.subscription.account_actions import IndividualSubscriptionAction
from core.subscription.models import JournalAccessSubscription


class JournalAccessSubscriptionCreateForm(forms.ModelForm):
    class Meta:
        model = AccountActionToken
        fields = [
            "email",
            "first_name",
            "last_name",
        ]

    def __init__(self, *args, **kwargs):
        self.management_subscription = kwargs.pop("management_subscription")
        super().__init__(*args, **kwargs)
        self.fields["email"].label = _("Courriel")
        self.fields["first_name"].label = _("Prénom")
        self.fields["last_name"].label = _("Nom")

    def clean_email(self):
        email = self.cleaned_data.get("email")

        # First checks if a pending subscription token already exists with this email address
        token_already_exists = (
            AccountActionToken.pending_objects.get_for_object(self.management_subscription)
            .filter(action=IndividualSubscriptionAction.name, email=email)
            .exists()
        )
        if token_already_exists:
            self.add_error(
                "email",
                _("Une proposition d'abonnement pour cette adresse courriel existe déjà"),
            )

        # Then checks if a subscription already exists for a user with this email address
        subscription_already_exists = JournalAccessSubscription.objects.filter(
            journal_management_subscription=self.management_subscription,
            user__email=email,
        ).exists()
        if subscription_already_exists:
            self.add_error("email", _("Un abonnement utilisant cette adresse courriel existe déjà"))

        return email

    def save(self, commit=True):
        instance = super(JournalAccessSubscriptionCreateForm, self).save(commit=False)
        instance.action = IndividualSubscriptionAction.name
        instance.content_object = self.management_subscription

        if commit:
            instance.save()

        return instance
