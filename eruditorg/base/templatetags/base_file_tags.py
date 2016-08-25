# -*- coding: utf-8 -*-

import mimetypes
import os

from django import template


register = template.Library()


@register.filter
def filename(value):
    """ Returns the filename of a ``django.core.files.File`` instance.

    This is necessary because the ``django.core.files.File.name`` attribute returns the name
    including the relative path from MEDIA_ROOT.
    """
    return os.path.basename(value.file.name)


@register.filter
def mimetype(value):
    """ Returns the type of a ``django.core.files.File`` instance. """
    content_type, _ = mimetypes.guess_type(value.file.name)
    return content_type or 'text/plain'
