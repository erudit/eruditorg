# -*- coding: utf-8 -*-

from django.conf.urls import include
from django.conf.urls import url


urlpatterns = [
    url(r'^sushi/', include('apps.webservices.sushi.urls', namespace='sushi')),
]
