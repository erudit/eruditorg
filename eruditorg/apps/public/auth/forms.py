# -*- coding: utf-8 -*-

from django.contrib.auth.forms import AuthenticationForm as BaseAuthenticationForm
from django.contrib.auth.forms import PasswordResetForm as BasePasswordResetForm
from django.utils.translation import ugettext_lazy as _
from core.email import Email


class AuthenticationForm(BaseAuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(AuthenticationForm, self).__init__(*args, **kwargs)

        # Updates some fields
        self.fields['username'].label = _("Nom d'utilisateur ou adresse e-mail")


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
