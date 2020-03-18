# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.utils.translation import gettext_lazy as _

from . import views

app_name = "subscription_ips"

urlpatterns = [
    url(r'^$', views.InstitutionIPAddressRangeListView.as_view(), name='list'),
    url(_(r'^ajout/$'), views.InstitutionIPAddressRangeCreateView.as_view(), name='create'),
    url(_(r'^(?P<pk>[0-9]+)/supprimer/$'),
        views.InstitutionIPAddressRangeDeleteView.as_view(), name='delete'),
]
