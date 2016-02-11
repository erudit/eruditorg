# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from . import views

urlpatterns = [
    url(_(r'^$'), views.PermissionsListView.as_view(), name='perm_list'),
    url(_(r'^ajout/$'), views.PermissionsCreateView.as_view(),
        name='perm_create'),
    url(_(r'(?P<pk>[0-9]+)/supprimer/$'),
        views.PermissionsDeleteView.as_view(), name='perm_delete'),
]
