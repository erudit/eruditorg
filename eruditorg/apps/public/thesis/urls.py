# -*- coding: utf-8 -*-

from django.conf.urls import include
from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from . import urls_compat
from . import views


urlpatterns = [
    url(r'^$', views.ThesisHomeView.as_view(), name='home'),
    url(_(r'^fond/(?P<pk>[\d-]+)/$'),
        views.ThesisCollectionHomeView.as_view(), name='collection_home'),

    # Compatibility URLs
    url('^', include(urls_compat.urlpatterns)),
]
