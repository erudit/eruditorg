# -*- coding: utf-8 -*-

from django.conf.urls import include
from django.conf.urls import url

from . import urls_compat
from . import views


urlpatterns = [
    url(r'^$', views.SearchResultsView.as_view(), name='results'),
    url(r'^avancee/$', views.AdvancedSearchView.as_view(), name='advanced_search'),
    url(r'^api/eruditdocuments/', views.EruditDocumentListAPIView.as_view(),
        name='eruditdocument-api-list'),

    # Compatibility URLs
    url('^', include(urls_compat.urlpatterns)),
]
