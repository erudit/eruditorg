# -*- coding: utf-8 -*-

from django.conf.urls import include
from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _


urlpatterns = [
    url(r'^', include('apps.public.journal.urls', namespace='journal')),

    url(_(r'^livre/'), include('apps.public.book.urls', namespace='book')),
    url(_(r'^recherche/'), include('apps.public.search.urls', namespace='search')),
    url(_(r'^these/'), include('apps.public.thesis.urls', namespace='thesis')),
]
