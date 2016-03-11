# -*- coding: utf-8 -*-

from django.conf.urls import include
from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _


urlpatterns = [
    url(r'^', include('apps.userspace.dashboard.urls')),

    url(_(r'^revue/'), include('apps.userspace.journal.urls', namespace='journal')),
    url(_(r'^reporting/'), include('apps.userspace.reporting.urls', namespace='reporting')),
]
