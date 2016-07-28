# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from . import views


urlpatterns = [
    url(r'^$', views.SavedCitationListView.as_view(), name='list'),
    url(_(r'^ajout/(?P<document_id>\d+)/$'),
        views.SavedCitationAddView.as_view(), name='add_citation'),
    url(_(r'^suppression/(?P<document_id>\d+)/$'),
        views.SavedCitationRemoveView.as_view(), name='remove_citation'),
]
