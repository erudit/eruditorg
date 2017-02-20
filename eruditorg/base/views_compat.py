# -*- coding: utf-8 -*-
from django.conf import settings
from django.http import HttpResponsePermanentRedirect
from django.views.generic import View


class RedirectToFallback(View):
    """
    Redirect a URL not supported by Refonte to retro.erudit.org
    """
    def get(self, request, *args, **kwargs):
        if request.path[0:4] == '/fr/' or request.path[0:4] == '/en/':
            retro_path = "{}{}".format(settings.FALLBACK_BASE_URL, request.path[3:])
        else:
            retro_path = "{}{}".format(settings.FALLBACK_BASE_URL, request.path)
        return HttpResponsePermanentRedirect(retro_path, )
