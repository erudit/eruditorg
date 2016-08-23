# -*- coding: utf-8 -*-

from django.conf.urls import include
from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from . import urls_compat
from . import views


urlpatterns = [
    url(r'^$', views.SearchUnitListView.as_view(), name='search_unit_list'),
    url(_(r'^(?P<code>[\w-]+)/$'), views.SearchUnitDetailView.as_view(),
        name='search_unit_detail'),
    url(_(r'^(?P<code>[\w-]+)/(?P<localid>[\w-]+)/$'),
        views.SearchUnitCollectionDetailView.as_view(), name='collection_detail'),

    # Compatibility URLs
    url('^', include(urls_compat.urlpatterns)),
]
