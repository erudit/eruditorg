# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm as BaseAuthenticationForm
from django.contrib.auth.forms import PasswordChangeForm as BasePasswordChangeForm
from django.contrib.auth.forms import PasswordResetForm as BasePasswordResetForm
from django.utils.translation import ugettext_lazy as _
from core.accounts.models import AbonnementProfile
from core.email import Email


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


class PasswordResetForm(BasePasswordResetForm):
    def get_users(self, email):
        """
        Overrides the  builtin `PasswordResetForm.get_users` method because it returns all the User
        instances who have usable passwords by default. We want to allow users without passwords
        (that have been imported from the old 'abonnement' database) to reset their passwords.
        """
        active_users = get_user_model()._default_manager.filter(
            email__iexact=email, is_active=True)
        return (u for u in active_users if u.has_usable_password() or
                AbonnementProfile.objects.filter(user=u).exists())

    def send_mail(
            self, subject_template_name, email_template_name, context, from_email, to_email,
            **kwargs):
        """
        Overrides the  builtin `PasswordResetForm.send_mail` method to use the `core.email.Email`
        tool.
        """
        email = Email(
            to_email,
            html_template=email_template_name,
            subject_template=subject_template_name,
            extra_context=context)
        email.send()
