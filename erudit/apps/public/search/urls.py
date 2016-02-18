# -*- coding: utf-8 -*-

# from django.conf.urls import include
from django.conf.urls import url

# from . import urls_compat
from . import views


urlpatterns = [
    # Compatibility URLs
    # url('^', include(urls_compat.urlpatterns)),
    url(r'^$', views.Search.as_view(), name="search"),
]
