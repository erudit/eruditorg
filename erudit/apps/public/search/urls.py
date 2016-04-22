# -*- coding: utf-8 -*-

from django.conf.urls import include
from django.conf.urls import url
from rest_framework import routers

from . import urls_compat
from . import views


search_api_router = routers.DefaultRouter()
search_api_router.register(r'eruditdocuments', views.EruditDocumentViewSet)


urlpatterns = [
    url(r'^$', views.Search.as_view(), name='search'),
    url(r'^api/', include(search_api_router.urls)),

    # Compatibility URLs
    url('^', include(urls_compat.urlpatterns)),
]
