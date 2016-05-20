# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from . import views

urlpatterns = [
    url(r'^$', views.InstitutionIPAddressRangeListView.as_view(), name='list'),
]
