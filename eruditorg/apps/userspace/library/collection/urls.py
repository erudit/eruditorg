# -*- coding: utf-8 -*-

from django.urls import re_path

from . import views

app_name = "collection"

urlpatterns = [
    re_path(r"^$", views.CollectionView.as_view(), name="landing"),
    re_path(r"^kbart2014/$", views.Kbart2014FileDownloadView.as_view(), name="kbart2014_download"),
]
