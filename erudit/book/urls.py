# -*- coding: utf-8 -*-

from django.conf.urls import include
from django.conf.urls import url

from . import urls_compat


urlpatterns = [
    # Compatibility URLs
    url('^', include(urls_compat.urlpatterns)),
]
