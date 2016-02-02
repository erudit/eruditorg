# -*- coding: utf-8 -*-

from django.conf.urls import include
from django.conf.urls import url

from . import urls_compat
from .views import JournalDetailView


urlpatterns = [
    url(r'^(?P<code>[\w-]+)/$', JournalDetailView.as_view(), name='journal-detail'),

    # Compatibility URLs
    url('^', include(urls_compat.urlpatterns)),
]
