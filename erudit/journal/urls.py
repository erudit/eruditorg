# -*- coding: utf-8 -*-

from django.conf.urls import url

from journal.views import JournalDetailView


urlpatterns = [
    url(r'^(?P<code>[\w-]+)/$', JournalDetailView.as_view(), name='journal-detail'),
]
