# -*- coding: utf-8 -*-

from django.conf.urls import include
from django.conf.urls import url
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from . import views
from .journal.urls import journal_urlpatterns

public_urlpatterns = ([
    url(r'^$', views.HomeView.as_view(), name='home'),

    url(_(r'^compte/'), include('apps.public.auth.urls')),
    url(_(r'^compte/actions/'), include(
        'apps.public.account_actions.urls', namespace='account_actions')),
    url(_(r'^notices/'), include('apps.public.citations.urls', namespace='citations')),
    url(_(r'^recherche/'), include('apps.public.search.urls', namespace='search')),
    url(_(r'^theses/'), include('apps.public.thesis.urls', namespace='thesis')),
    url(_(r'^livres/'), include('apps.public.book.urls', namespace='book')),
    url(_(r'^identite/$'), TemplateView.as_view(template_name='public/brand_assets.html'),
        name='brand_assets'),
    url(_(r'^20ans/$'), TemplateView.as_view(template_name='public/20_years.html'),
        name='20_years'),

    # The journal URLs are at the end of the list because some of them are catchalls.
    url(r'^', include(journal_urlpatterns)),
], 'public')
