# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.forms import AuthenticationForm as BaseAuthenticationForm
from django.contrib.auth.forms import PasswordResetForm as BasePasswordResetForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from core.email import Email


class AuthenticationForm(BaseAuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(AuthenticationForm, self).__init__(*args, **kwargs)

        # Updates some fields
        self.fields['username'].label = _("Nom d'utilisateur ou adresse e-mail")


class UserPersonalDataForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', )


class UserParametersForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', )

    def __init__(self, *args, **kwargs):
        super(UserParametersForm, self).__init__(*args, **kwargs)
        # Updates some fields
        self.fields['email'].required = True

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            self.add_error('email', _('Cette adresse e-mail est déjà utilisée'))
        return email


class PasswordResetForm(BasePasswordResetForm):
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
