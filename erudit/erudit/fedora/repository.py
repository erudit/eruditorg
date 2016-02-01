# -*- coding: utf-8 -*-

from eulfedora.server import Repository

from erudit.fedora.conf import settings


repo = Repository(
    settings.FEDORA_ROOT, settings.FEDORA_USER, settings.FEDORA_PASSWORD)
api = repo.api
