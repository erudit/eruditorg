# -*- coding: utf-8 -*-

from django.conf.urls import include
from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from .views import UserspaceHomeView


urlpatterns = [
    url(r'^$', UserspaceHomeView.as_view(), name='dashboard'),

    url(_(r'^revue/'), include('apps.userspace.journal.urls', namespace='journal')),
    url(_(r'^bibliotheque/'), include('apps.userspace.library.urls', namespace='library')),
    url(_(r'^reporting/'), include('apps.userspace.reporting.urls', namespace='reporting')),
]
