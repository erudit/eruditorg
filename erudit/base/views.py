# -*- coding: utf-8 -*-

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic import View


class DummyView(View):
    """
    Just a dummy view to use with retro-compatible urls during development.
    """
    def get(self, request, *args, **kwargs):  # pragma: no cover
        if settings.DEBUG:
            return HttpResponse(request.path, content_type='text/plain')
        return redirect('/')
