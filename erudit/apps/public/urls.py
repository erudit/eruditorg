# -*- coding: utf-8 -*-

from django.conf.urls import include
from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from . import views


urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name='home'),

    url(_(r'^livre/'), include('apps.public.book.urls', namespace='book')),
    url(_(r'^recherche/'), include('apps.public.search.urls', namespace='search')),
    url(_(r'^these/'), include('apps.public.thesis.urls', namespace='thesis')),

    url(r'^', include('apps.public.journal.urls', namespace='journal')),
]
