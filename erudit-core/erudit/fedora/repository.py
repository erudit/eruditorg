# -*- coding: utf-8 -*-

from eulfedora.api import REST_API
from eulfedora.server import Repository

from ..conf import settings


repo = Repository(settings.FEDORA_ROOT, settings.FEDORA_USER, settings.FEDORA_PASSWORD)

api = repo.api
rest_api = REST_API(settings.FEDORA_ROOT, settings.FEDORA_USER, settings.FEDORA_PASSWORD)
