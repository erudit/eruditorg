# -*- coding: utf-8 -*-

from django.conf.urls import include
from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from . import urls_compat
from . import views


urlpatterns = [
    url(r'^$', views.SearchUnitListView.as_view(), name='search_unit_list'),

    # Compatibility URLs
    url('^', include(urls_compat.urlpatterns)),
]
