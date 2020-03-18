# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.utils.translation import gettext_lazy as _

from . import views

app_name = "members"

urlpatterns = [
    url(r'^$', views.OrganisationMemberListView.as_view(), name='list'),
    url(_(r'^ajout/$'), views.OrganisationMemberCreateView.as_view(), name='create'),
    url(_(r'^supprimer/(?P<pk>[0-9]+)/$'),
        views.OrganisationMemberDeleteView.as_view(), name='delete'),
    url(_(r'^annuler/(?P<pk>[0-9]+)/$'),
        views.OrganisationMemberCancelView.as_view(), name='cancel'),
]
