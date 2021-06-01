# -*- coding: utf-8 -*-

from django.urls import re_path

from . import views

app_name = "subscription_information"

urlpatterns = [
    re_path(r"^$", views.SubscriptionInformationUpdateView.as_view(), name="update"),
]
