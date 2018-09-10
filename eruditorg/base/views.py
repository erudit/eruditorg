# -*- coding: utf-8 -*-

from django.conf import settings
from django.http import (
    HttpResponse,
    Http404,
)
from django.shortcuts import redirect
from django.core.urlresolvers import (
    reverse,
    resolve,
)
from django.utils.translation import get_language
from django.views.generic import View, RedirectView

from base.context_managers import switch_language
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

    def get_redirect_url(self, *args, **kwargs):
        self.activate_legacy_language(*args, **kwargs)
        return reverse(self.pattern_name)


def canonical_journal_urls_view(request):
    language = get_language()
    default_lang_url = '/{}{}'.format(settings.LANGUAGE_CODE, request.path)
    if default_lang_url[-1] != '/':
        default_lang_url += '/'
    supported_languages_codes = [l[0] for l in settings.LANGUAGES]
    if language == settings.LANGUAGE_CODE or language not in supported_languages_codes:
        return redirect(default_lang_url)

    with switch_language(settings.LANGUAGE_CODE):
        resolver_match = resolve(default_lang_url)
    if not resolver_match or not resolver_match.url_name or not resolver_match.namespace:
        raise Http404
    args = resolver_match.args
    kwargs = resolver_match.kwargs.copy()
    i18n_url = reverse(
        ':'.join([resolver_match.namespace, resolver_match.url_name]),
        args=args, kwargs=kwargs)
    return redirect(i18n_url)
