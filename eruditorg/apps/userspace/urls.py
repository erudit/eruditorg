# -*- coding: utf-8 -*-

from django.conf.urls import include
from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from .views import UserspaceHomeView

app_name = "userspace"

urlpatterns = [
    url(r'^$', UserspaceHomeView.as_view(), name='dashboard'),

    url(_(r'^revue/'), include('apps.userspace.journal.urls')),
    url(_(r'^bibliotheque/'), include('apps.userspace.library.urls')),
    url(_(r'^reporting/'), include('apps.userspace.reporting.urls')),
]
