# -*- coding: utf-8 -*-

from django.conf.urls import url

from . import views

app_name = "collection"

urlpatterns = [
    url(r'^$', views.CollectionView.as_view(), name='landing'),
    url(r'^kbart2014/$', views.Kbart2014FileDownloadView.as_view(), name='kbart2014_download'),
]
