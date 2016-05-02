# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.views.generic import RedirectView

from base.views import DummyView


unsupported_patterns = [
    r'^(?P<code>[\w-]+)/?$',
]

urlpatterns = [
    url(r'^index\.html?$',
        RedirectView.as_view(pattern_name='public:search:search', permanent=True))
]

urlpatterns += [url(pattern_re, DummyView.as_view()) for pattern_re in unsupported_patterns]
