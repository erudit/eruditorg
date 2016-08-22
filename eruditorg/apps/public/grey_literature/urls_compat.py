# -*- coding: utf-8 -*-

from django.conf.urls import url

from base.views import DummyView


unsupported_patterns = [
]

urlpatterns = [
]

urlpatterns += [url(pattern_re, DummyView.as_view()) for pattern_re in unsupported_patterns]
