# -*- coding: utf-8 -*-

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import (
    reverse,
)
from django.views.generic import View, RedirectView

from .viewmixins import ActivateLegacyLanguageViewMixin


class DummyView(View):
    """
    Just a dummy view to use with retro-compatible urls during development.
    """
    def get(self, request, *args, **kwargs):  # pragma: no cover
        if settings.DEBUG:
            return HttpResponse(request.path, content_type='text/plain')
        return redirect('/')


class RedirectRetroUrls(RedirectView, ActivateLegacyLanguageViewMixin):

    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        self.activate_legacy_language(*args, **kwargs)
        return reverse(self.pattern_name)
