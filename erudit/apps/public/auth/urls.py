# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from . import views


urlpatterns = [
    # Sign in / sign out
    url(_(r'^connexion/$'), 'django.contrib.auth.views.login',
        {'template_name': 'public/auth/login.html'}, name='login'),
    url(_(r'^deconnexion/$'), 'django.contrib.auth.views.logout',
        {'next_page': '/'}, name='logout'),

    # Password change

    # Password reset
    url(_(r'^mot-de-passe/reset/$'), 'django.contrib.auth.views.password_reset',
        {'template_name': 'public/auth/password_reset_form.html',
         'post_reset_redirect': 'public:auth:password_reset_done', }, name='password_reset'),
    url(_(r'^mot-de-passe/reset/done/$'), 'django.contrib.auth.views.password_reset_done',
        {'template_name': 'public/auth/password_reset_done.html'}, name='password_reset_done'),
    url(_(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$'),
        'django.contrib.auth.views.password_reset_confirm',
        {'template_name': 'public/auth/password_reset_confirm.html',
         'post_reset_redirect': 'public:auth:password_reset_complete', },
        name='password_reset_confirm'),
    url(_(r'^reset/done/$'), 'django.contrib.auth.views.password_reset_complete',
        {'template_name': 'public/auth/password_reset_complete.html'},
        name='password_reset_complete'),
]
