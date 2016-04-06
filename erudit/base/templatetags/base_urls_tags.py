# -*- coding: utf-8 -*-

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
    args = resolver_match.args
    kwargs = resolver_match.kwargs.copy()
    with switch_language(langcode):
        i18n_url = reverse(
            ':'.join([resolver_match.namespace, resolver_match.url_name]),
            args=args, kwargs=kwargs)

    return i18n_url
