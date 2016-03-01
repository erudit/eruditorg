# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from . import views


urlpatterns = [
    url(r'^$', views.ReportingHomeView.as_view(), name='home'),
    url(_(r'^csv/$'), views.ReportingCsvView.as_view(), name='csv-export'),
]
