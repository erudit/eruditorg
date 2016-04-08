# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.forms import AuthenticationForm as BaseAuthenticationForm
from django.contrib.auth.forms import PasswordChangeForm as BasePasswordChangeForm
from django.utils.translation import ugettext_lazy as _

from core.accounts.models import AbonnementProfile


class AuthenticationForm(BaseAuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(AuthenticationForm, self).__init__(*args, **kwargs)

        # Updates some fields
        self.fields['username'].label = _("Nom d'utilisateur ou adresse e-mail")


class PasswordChangeForm(BasePasswordChangeForm):
    def clean_old_password(self):
        """
        Validates that the old_password field is correct.
        """
        old_password = self.cleaned_data.get('old_password')

        # Special case: the User is associated with an AbonnementProfile instance
        abonnementprofile = AbonnementProfile.objects.filter(user=self.user).first()
        if abonnementprofile and abonnementprofile.sha1(old_password) != abonnementprofile.password:
            raise forms.ValidationError(
                self.error_messages['password_incorrect'], code='password_incorrect')
        elif not abonnementprofile:
            return super(PasswordChangeForm, self).clean_old_password()

        return old_password

    def save(self, commit=True):
        instance = super(PasswordChangeForm, self).save(commit)

        abonnementprofile_qs = AbonnementProfile.objects.filter(user=instance)
        if commit and abonnementprofile_qs.exists():
            # Removes the AbonnementProfile instance associated with the user if it exists!
            abonnementprofile_qs.delete()

        return instance
