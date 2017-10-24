# -*- coding: utf-8 -*-

from django.conf.urls import url

from apps.userspace.library.stats.legacy import views

urlpatterns = [
    url(r'^$', views.StatsLandingView.as_view(), name='landing'),
]
