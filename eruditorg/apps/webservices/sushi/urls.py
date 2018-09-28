# -*- coding: utf-8 -*-

from django.conf.urls import url

from . import views

app_name = "sushi"

urlpatterns = [
    url(r'^$', views.SushiWebServiceView.as_view(), name='entrypoint'),
]
