# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.views.generic import RedirectView

from base.views import DummyView


unsupported_patterns = [
    r'^iderudit/(?P<code>[\w-]+)$',

    r'^revue/(?P<code>[\w-]+)/rss.xml$',
    r'^revue/(?P<code>[\w-]+)/(?P<year>\d{4})/(?P<v>[\w-]+)/(?P<issue>[\w-]+)/?$',
    r'^revue/(?P<code>[\w-]+)/(?P<year>\d{4})/(?P<v>[\w-]+)/(?P<issue>[\w-]+)/index.html?$',
    (r'^revue/(?P<code>[\w-]+)/(?P<year>\d{4})/(?P<v>[\w-]+)/' +
     '(?P<issue>[\w-]+)/(?P<article>[\w-]+).html?$'),
    r'^revue/(?P<code>[\w-]+)/auteurs.html?$',
    r'^revue/(?P<code>[\w-]+)/thematique.html?$',
    r'^revue/(?P<code>[\w-]+)/apropos.html?$',
    r'^revue/redirection/(?P<code>[\w-]+)/',

    r'^culture/(?P<code>[\w-]+)/$',
    r'^culture/(?P<code>[\w-]+)/index.html?$',
    r'^culture/(?P<code>[\w-]+)/rss.xml$',
    r'^culture/(?P<code>[\w-]+)/(?P<year>\d{4})/(?P<v>[\w-]+)/(?P<issue>[\w-]+)/?$',
    r'^culture/(?P<code>[\w-]+)/(?P<year>\d{4})/(?P<v>[\w-]+)/(?P<issue>[\w-]+)/index.html?$',
    (r'^culture/(?P<code>[\w-]+)/(?P<year>\d{4})/(?P<v>[\w-]+)/' +
     '(?P<issue>[\w-]+)/(?P<article>[\w-]+).html?$'),
    r'^culture/(?P<code>[\w-]+)/auteurs.html?$',
    r'^culture/(?P<code>[\w-]+)/thematique.html?$',

    r'^feuilletage/index.html?$',
    r'^feuilletage_(?P<code1>[\w-]+)\.(?P<code2>[\w-]+)@(?P<id>[0-9]+)$',
    (r'^feuilletage_(?P<code1>[\w-]+)\.(?P<code2>[\w-]+)@(?P<id>[0-9]+)'
     '(?:\&(?P<key>[\w-]+)=(?P<val>[\w-]+))*$'),
]

urlpatterns = [
    url(r'^revue/(?P<code>[\w-]+)/$',
        RedirectView.as_view(pattern_name='journal:journal-detail', permanent=True)),
    url(r'^revue/(?P<code>[\w-]+)/index.html?$',
        RedirectView.as_view(pattern_name='journal:journal-detail', permanent=True)),
]

urlpatterns += [url(pattern_re, DummyView.as_view()) for pattern_re in unsupported_patterns]
