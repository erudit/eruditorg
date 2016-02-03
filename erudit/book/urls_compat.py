# -*- coding: utf-8 -*-

from django.conf.urls import url

from base.views import DummyView


unsupported_patterns = [
    r'^$',
    r'^index.html?$',
    r'^(?P<code>[\w-]+)/index.html?$',
    r'^(?P<code>[\w-]+)/(?P<year>\d{4})/index.html?$',
    r'^(?P<code>[\w-]+)/(?P<year>\d{4}-\d)/index.html?$',
    r'^(?P<code>[\w-]+)/(?P<year>\d{4})/(?P<litcode>[\w-]+).html?$',
    r'^(?P<code>[\w-]+)/(?P<year>\d{4})/(?P<litcode>[\w-]+).lit$',
]

urlpatterns = [url(pattern_re, DummyView.as_view()) for pattern_re in unsupported_patterns]
