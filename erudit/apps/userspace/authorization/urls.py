# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from . import views

urlpatterns = [
    url(r'^$', views.AuthorizationUserView.as_view(), name='authorization_list'),
    url(_(r'^ajout/$'), views.AuthorizationCreateView.as_view(), name='authorization_create'),
    url(_(r'(?P<pk>[0-9]+)/supprimer/$'),
        views.AuthorizationDeleteView.as_view(), name='authorization_delete'),
]
