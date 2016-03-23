# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from . import views


urlpatterns = [
    url(_(r'^acces/$'),
        views.IndividualJournalAccessSubscriptionListView.as_view(), name='list'),
    url(_(r'^acces/ajout/'),
        views.IndividualJournalAccessSubscriptionCreateView.as_view(), name='create'),
    url(_(r'^acces/supprimer/(?P<pk>[0-9]+)/$'),
        views.IndividualJournalAccessSubscriptionDeleteView.as_view(),
        name='delete'),
    url(_(r'^acces/(?P<pk>[0-9]+)/$'),
        views.IndividualJournalAccessSubscriptionUpdateView.as_view(), name='update'),
]
