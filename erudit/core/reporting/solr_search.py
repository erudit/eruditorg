# -*- coding: utf-8 -*-

"""
This module defines the Solr search object used to retrieve data in order to
present statistics on Érudit articles.

This is based on the use of pysolr.
"""

import pysolr

from .conf import settings as reporting_settings


# This is the object that will be used to query the Article index.
search = pysolr.Solr(reporting_settings.SOLR_ROOT, timeout=10)
