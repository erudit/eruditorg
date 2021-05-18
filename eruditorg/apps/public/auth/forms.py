# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.forms import AuthenticationForm as BaseAuthenticationForm
from django.contrib.auth.forms import PasswordResetForm as BasePasswordResetForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.translation import gettext_lazy as _
from core.email import Email


class AuthenticationForm(BaseAuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(AuthenticationForm, self).__init__(*args, **kwargs)

        # Updates some fields
        self.fields["username"].label = _("Nom d'utilisateur ou adresse courriel")


class UserPersonalDataForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
        )


class UserParametersForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "username",
            "email",
        )

    def __init__(self, *args, **kwargs):
        super(UserParametersForm, self).__init__(*args, **kwargs)
        # Updates some fields
        self.fields["email"].required = True

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            self.add_error("email", _("Cette adresse courriel est déjà utilisée"))
        return email


class PasswordResetForm(BasePasswordResetForm):
    def send_mail(
        self, subject_template_name, email_template_name, context, from_email, to_email, **kwargs
    ):
        """
        Overrides the  builtin `PasswordResetForm.send_mail` method to use the `core.email.Email`
        tool.
        """
        email = Email(
            to_email,
            html_template=email_template_name,
            subject_template=subject_template_name,
            extra_context=context,
            tag="www-reinitialisation-mot-de-passe",
        )
        email.send()

    def get_users(self, email):
        """Given an email, return matching user(s) who should receive a reset.

        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.
        """
        active_users = get_user_model()._default_manager.filter(email__iexact=email, is_active=True)
        return [u for u in active_users]

    def save(
        self,
        domain_override=None,
        subject_template_name="emails/auth/password_reset_registered_email_subject.txt",
        email_template_name="emails/auth/password_reset_registered_email.html",
        use_https=False,
        token_generator=default_token_generator,
        from_email=None,
        request=None,
        html_email_template_name=None,
        extra_email_context=None,
    ):
        """
        If the email belongs to a registered user, generate a one-use only link for resetting
        password and send it to the user. If the email does not belong to a registered user,
        send an email to that email address informing that the password reset failed.
        """
        email = self.cleaned_data["email"]
        if self.get_users(email):
            # Registered user
            # Check if there are any registered users for the entered email
            return super().save(
                domain_override,
                subject_template_name,
                email_template_name,
                use_https,
                token_generator,
                from_email,
                request,
                html_email_template_name,
                extra_email_context,
            )
        else:
            # Unregistered user
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            context = {
                "email": email,
                "domain": domain,
                "site_name": site_name,
                "uid": None,
                "user": None,
                "token": None,
                "protocol": "https" if use_https else "http",
                **(extra_email_context or {}),
            }
            self.send_mail(
                "emails/auth/password_reset_unregistered_email_subject.txt",
                "emails/auth/password_reset_unregistered_email.html",
                context,
                from_email,
                email,
                html_email_template_name=html_email_template_name,
            )
