# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from . import views


urlpatterns = [
    url(r'^$', views.StatsLandingView.as_view(), name='landing'),
    url(_(r'^rapport/jr1/csv/$'),
        views.CounterJournalReport1CsvView.as_view(), name='jr1-csv-report'),
    url(_(r'^rapport/jr1-goa/csv/$'),
        views.CounterJournalReport1GOACsvView.as_view(), name='jr1-goa-csv-report'),
]
