# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from . import views

app_name = "reporting"

urlpatterns = [
    url(r'^$', views.ReportingHomeView.as_view(), name='home'),
    url(_(r'^csv/numero/$'), views.ReportingIssueCsvView.as_view(), name='csv_issue_export'),
    url(_(r'^csv/journal/$'), views.ReportingJournalCsvView.as_view(), name='csv_journal_export'),
]
