# -*- coding: utf-8 -*-

from django.urls import re_path
from django.utils.translation import gettext_lazy as _

from . import views

app_name = "account_actions"

urlpatterns = [
    re_path(_(r"^(?P<key>[\w-]+)/$"), views.AccountActionLandingView.as_view(), name="landing"),
    re_path(_(r"^(?P<key>[\w-]+)/c/$"), views.AccountActionConsumeView.as_view(), name="consume"),
    re_path(
        _(r"^(?P<key>[\w-]+)/inscription/$"),
        views.AccountActionRegisterView.as_view(),
        name="register",
    ),
]
