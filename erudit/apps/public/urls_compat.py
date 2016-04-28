# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.views.generic import RedirectView


urlpatterns = [
    url(r'^client/login.jsp$',
        RedirectView.as_view(pattern_name='public:auth:login', permanent=True)),
    url(r'^client/getNewPassword.jsp$',
        RedirectView.as_view(pattern_name='public:auth:password_reset', permanent=True)),
    url(r'^client/updatePassword.jsp$',
        RedirectView.as_view(pattern_name='public:auth:password_reset', permanent=True)),
]
