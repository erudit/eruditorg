from eulfedora.server import Repository

from ..conf import settings


repo = Repository(settings.FEDORA_ROOT, settings.FEDORA_USER, settings.FEDORA_PASSWORD)
api = repo.api
