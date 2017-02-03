# -*- coding: utf-8 -*-

from urllib.parse import parse_qsl
from urllib.parse import urlencode
from urllib.parse import urlparse

from django import template
from django.core.urlresolvers import reverse

from base.context_managers import switch_language

register = template.Library()


@register.simple_tag(takes_context=True)
def trans_current_url(context, langcode):
    """ Returns the current URL translated in the passed language. """
    request = context.get('request')

    # Reverses the current URL in the considered language
    resolver_match = request.resolver_match
    if not resolver_match:
        return None
    args = resolver_match.args
    kwargs = resolver_match.kwargs.copy()
    with switch_language(langcode):
        i18n_url = reverse(
            ':'.join([resolver_match.namespace, resolver_match.url_name]),
            args=args, kwargs=kwargs)

    return i18n_url


@register.simple_tag(takes_context=True)
def get_full_path_with_overrides(context, **kwargs):
    """ Returns the current full path and inserts keyword arguments into the final path. """
    request = context.get('request')
    fpath = request.get_full_path()
    fpath_parsed = urlparse(fpath)
    qsdict = dict(parse_qsl(fpath_parsed.query))
    qsdict.update(kwargs)
    qs = urlencode(qsdict)
    return fpath_parsed.path + '?' + qs
