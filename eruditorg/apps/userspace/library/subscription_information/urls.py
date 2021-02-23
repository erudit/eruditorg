# -*- coding: utf-8 -*-

from django.conf.urls import url

from . import views

app_name = "subscription_information"

urlpatterns = [
    url(r"^$", views.SubscriptionInformationUpdateView.as_view(), name="update"),
]
