# -*- coding: utf-8 -*-

from django.urls import re_path

from apps.userspace.library.stats import views

app_name = "stats"

urlpatterns = [
    re_path(r"^$", views.StatsLandingView.as_view(), name="landing"),
]
