# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.views.generic import RedirectView

from base.views import DummyView


unsupported_patterns = [
]

urlpatterns = [
    url(r'^liste.html?$', RedirectView.as_view(pattern_name='public:thesis:home', permanent=True)),
    url(r'^index.html?$', RedirectView.as_view(pattern_name='public:thesis:home', permanent=True)),
]

urlpatterns += [url(pattern_re, DummyView.as_view()) for pattern_re in unsupported_patterns]
