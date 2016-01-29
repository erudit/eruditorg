# -*- coding: utf-8 -*-

from django.conf import settings
from eulfedora.server import Repository


repo = Repository(
    settings.FEDORA_ROOT, settings.FEDORA_USER, settings.FEDORA_PASSWORD)
