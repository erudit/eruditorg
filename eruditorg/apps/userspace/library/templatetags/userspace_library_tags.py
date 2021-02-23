# -*- coding: utf-8 -*-

from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag(takes_context=True)
def library_url(context, organisation):
    """ Resolves the pattern of the current URL for the given Organisation instance. """
    request = context.get("request")
    resolver_match = request.resolver_match
    args = resolver_match.args
    kwargs = resolver_match.kwargs.copy()
    kwargs.update({"organisation_pk": organisation.pk})
    return reverse(
        ":".join([resolver_match.namespace, resolver_match.url_name]), args=args, kwargs=kwargs
    )
