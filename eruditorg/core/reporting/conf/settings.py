# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


SOLR_ROOT = getattr(settings, 'SOLR_ROOT', None)
if SOLR_ROOT is None:  # pragma: no cover
    ImproperlyConfigured(
        'You must set the SOLR_ROOT setting to use the \'reporting\' module')
