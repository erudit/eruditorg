# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from . import views


urlpatterns = [
    url(_(r'^information/$'),
        views.JournalInformationDispatchView.as_view(), name='journal-information'),
    url(_(r'^information/liste/$'),
        views.JournalInformationListView.as_view(), name='journal-information-list'),
    url(_(r'^information/(?P<code>[\w-]+)/edition/$'),
        views.JournalInformationUpdateView.as_view(), name='journal-information-update'),
]
