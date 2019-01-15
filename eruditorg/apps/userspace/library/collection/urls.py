# -*- coding: utf-8 -*-

from django.conf.urls import url

from . import views

app_name = "collection"

urlpatterns = [
    url(r'^$', views.CollectionView.as_view(), name='landing'),
    url(r'oclc/(?P<format>\w+)', views.CollectionOclcView.as_view(), name='oclc')
]
