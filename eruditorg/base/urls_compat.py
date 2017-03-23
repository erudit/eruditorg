# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.conf.urls import include
from django.views.generic import RedirectView

from .views import DummyView, RedirectRetroUrls

urlpatterns = [
    url(r'^(?:(?P<lang>[\w-]+)/)?', include([
        url(r'^index.html?$', RedirectView.as_view(pattern_name='home', permanent=True)),
        url(r'^revue/?$', RedirectRetroUrls.as_view(
            pattern_name='public:journal:journal_list',
            permanent=True)),
        url(r'^(?:(?P<lang>[\w-]+)/)?culture/?$', RedirectRetroUrls.as_view(
            pattern_name='public:journal:journal_list',
            permanent=True)),
        url(r'^(?:(?P<lang>[\w-]+)/)?these/$', RedirectRetroUrls.as_view(
            pattern_name='public:thesis:home',
            permanent=True)),
        url(r'^(?:(?P<lang>[\w-]+)/)?abonnement/login\.jsp$',
            RedirectRetroUrls.as_view(pattern_name='login', permanent=True)),
        url(r'^(?:(?P<lang>[\w-]+)/)?abonnement/oublierPassword\.jsp$',
            RedirectRetroUrls.as_view(pattern_name='password_reset', permanent=True)),
        url(r'^(?:(?P<lang>[\w-]+)/)?abonnement/modifierPassword\.jsp$',
            RedirectRetroUrls.as_view(pattern_name='password_change', permanent=True)),
        url(r'^(?:(?P<lang>[\w-]+)/)?client/login\.jsp$',
            RedirectRetroUrls.as_view(pattern_name='login', permanent=True)),
        url(r'^(?:(?P<lang>[\w-]+)/)?client/getNewPassword\.jsp$',
            RedirectRetroUrls.as_view(pattern_name='password_reset', permanent=True)),
        url(r'^(?:(?P<lang>[\w-]+)/)?client/updatePassword\.jsp$',
            RedirectRetroUrls.as_view(pattern_name='password_change', permanent=True)),

        url(r'^rss.xml$', DummyView.as_view()),
    ]),),
]
