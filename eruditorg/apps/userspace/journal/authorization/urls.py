# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from . import views

app_name = "authorization"

urlpatterns = [
    url(r'^$', views.AuthorizationUserView.as_view(), name='list'),
    url(_(r'^ajout/$'), views.AuthorizationCreateView.as_view(), name='create'),
    url(_(r'^(?P<pk>[0-9]+)/supprimer/$'),
        views.AuthorizationDeleteView.as_view(), name='delete'),
]
