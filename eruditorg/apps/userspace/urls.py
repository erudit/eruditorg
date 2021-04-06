# -*- coding: utf-8 -*-

from django.urls import include, re_path
from django.utils.translation import gettext_lazy as _

from .views import UserspaceHomeView

app_name = "userspace"

urlpatterns = [
    re_path(r"^$", UserspaceHomeView.as_view(), name="dashboard"),
    re_path(_(r"^revue/"), include("apps.userspace.journal.urls")),
    re_path(_(r"^bibliotheque/"), include("apps.userspace.library.urls")),
]
