# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.views.generic import RedirectView

from .views import DummyView
from .views_compat import RedirectToFallback


urlpatterns = [
    url(r'^index.html?$',
        RedirectView.as_view(url='/', permanent=True)),

    url(r'^abonnement/login\.jsp$',
        RedirectView.as_view(pattern_name='login', permanent=True)),
    url(r'^abonnement/oublierPassword\.jsp$',
        RedirectView.as_view(pattern_name='password_reset', permanent=True)),
    url(r'^abonnement/modifierPassword\.jsp$',
        RedirectView.as_view(pattern_name='password_change', permanent=True)),
    url(r'^client/login\.jsp$',
        RedirectView.as_view(pattern_name='login', permanent=True)),
    url(r'^client/getNewPassword\.jsp$',
        RedirectView.as_view(pattern_name='password_reset', permanent=True)),
    url(r'^client/updatePassword\.jsp$',
        RedirectView.as_view(pattern_name='password_change', permanent=True)),

    url(r'^rss.xml$', DummyView.as_view()),

    # Redirect not supported URLs to retro.erudit.org
    url(r'^.*$', RedirectToFallback.as_view(), ),
]
