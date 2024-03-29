# -*- coding: utf-8 -*-

from django.urls import re_path
from django.contrib.auth import views as auth_views
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy

from . import forms
from . import views

app_name = "auth"

urlpatterns = [
    # Sign in / sign out
    re_path(
        _(r"^connexion/$"),
        views.LoginView.as_view(
            template_name="public/auth/login.html", authentication_form=forms.AuthenticationForm
        ),
        name="login",
    ),
    re_path(_(r"^deconnexion/$"), auth_views.LogoutView.as_view(next_page="/"), name="logout"),
    re_path(_(r"^bienvenue/$"), views.UserLoginLandingRedirectView.as_view(), name="landing"),
    # Parameters & personal data
    re_path(
        _(r"^donnees-personnelles/$"),
        views.UserPersonalDataUpdateView.as_view(),
        name="personal_data",
    ),
    re_path(_(r"^parametres/$"), views.UserParametersUpdateView.as_view(), name="parameters"),
    # Password change
    re_path(_(r"^mot-de-passe/$"), views.UserPasswordChangeView.as_view(), name="password_change"),
    # Password reset
    re_path(
        _(r"^mot-de-passe/reinitialisation/$"),
        auth_views.PasswordResetView.as_view(
            template_name="public/auth/password_reset_form.html",
            email_template_name="emails/auth/password_reset_registered_email.html",
            subject_template_name="emails/auth/password_reset_registered_email_subject.txt",
            form_class=forms.PasswordResetForm,
            success_url=reverse_lazy("public:auth:password_reset_done"),
        ),
        name="password_reset",
    ),
    re_path(
        _(r"^mot-de-passe/reinitialisation/termine/$"),
        auth_views.PasswordResetDoneView.as_view(
            template_name="public/auth/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    re_path(
        _(r"^reinitialisation/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]+-[0-9A-Za-z]+)/$"),
        auth_views.PasswordResetConfirmView.as_view(
            template_name="public/auth/password_reset_confirm.html",
            success_url=reverse_lazy("public:auth:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    re_path(
        _(r"^reinitialisation/termine/$"),
        auth_views.PasswordResetCompleteView.as_view(
            template_name="public/auth/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
