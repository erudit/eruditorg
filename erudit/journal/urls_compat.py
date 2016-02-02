# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.views.generic import RedirectView

from base.views import DummyView


unsupported_patterns = [
    r'^(?P<code>[\w-]+)/rss.xml$',
    r'^(?P<code>[\w-]+)/(?P<year>\d{4})/(?P<v>[\w-]+)/(?P<issue>[\w-]+)/?$',
    r'^(?P<code>[\w-]+)/(?P<year>\d{4})/(?P<v>[\w-]+)/(?P<issue>[\w-]+)/index.html?$',
    r'^(?P<code>[\w-]+)/(?P<year>\d{4})/(?P<v>[\w-]+)/(?P<issue>[\w-]+)/(?P<article>[\w-]+).html?$',
    r'^(?P<code>[\w-]+)/auteurs.html?$',
    r'^(?P<code>[\w-]+)/thematique.html?$',
    r'^(?P<code>[\w-]+)/apropos.html?$',
    r'^redirection/(?P<code>[\w-]+)/',
]

urlpatterns = [
    url(r'^(?P<code>[\w-]+)/index.html?$',
        RedirectView.as_view(pattern_name='journal:journal-detail', permanent=True)),
]

urlpatterns += [url(pattern_re, DummyView.as_view()) for pattern_re in unsupported_patterns]
