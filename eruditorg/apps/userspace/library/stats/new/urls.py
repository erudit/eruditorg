# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from apps.userspace.library.stats.new import views
from apps.userspace.library.stats.common.views import StatsLandingView

app_name = "stats"

urlpatterns = [
    url(r'^$', StatsLandingView.as_view(), name='landing'),
    url(_(r'^rapport/jr1/csv/$'),
        views.CounterJournalReport1CsvView.as_view(), name='jr1-csv-report'),
    url(_(r'^rapport/jr1-goa/csv/$'),
        views.CounterJournalReport1GOACsvView.as_view(), name='jr1-goa-csv-report'),
    url(_(r'^rapport/jr1/xml/$'),
        views.CounterJournalReport1XmlView.as_view(), name='jr1-xml-report'),
    url(_(r'^rapport/jr1-goa/xml/$'),
        views.CounterJournalReport1GOAXmlView.as_view(), name='jr1-goa-xml-report'),
]
