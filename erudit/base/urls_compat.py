# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _
from django.views.generic import RedirectView


urlpatterns = [
    url(_(r'^abonnement/login\.jsp$'),
        RedirectView.as_view(pattern_name='login', permanent=True)),
    url(_(r'^abonnement/oublierPassword\.jsp$'),
        RedirectView.as_view(pattern_name='password_reset', permanent=True)),
    url(_(r'^abonnement/modifierPassword\.jsp$'),
        RedirectView.as_view(pattern_name='password_change', permanent=True)),
]
