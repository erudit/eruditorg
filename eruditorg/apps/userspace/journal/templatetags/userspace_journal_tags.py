# -*- coding: utf-8 -*-

from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag(takes_context=True)
def journal_url(context, journal):
    """ Resolves the pattern of the current URL for the given Journal instance and returns it. """
    request = context.get('request')
    resolver_match = request.resolver_match
    args = resolver_match.args
    kwargs = resolver_match.kwargs.copy()
    kwargs.update({'journal_pk': journal.pk})
    return reverse(
        ':'.join([resolver_match.namespace, resolver_match.url_name]), args=args, kwargs=kwargs)
