# -*- coding: utf-8 -*-

import argparse
import time
from urllib.parse import urlparse
from urllib.parse import urlunparse

from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
import requests


class Command(BaseCommand):
    """ Tests compat URLs using a file listing one URL to test per line. """

    help = "Tests compat URLs"

    def add_arguments(self, parser):
        parser.add_argument("urls_file", type=argparse.FileType("r"))
        parser.add_argument("sleep_time", nargs="?", type=float, default=2)

    def handle(self, *args, **options):
        urls_file = options.get("urls_file")
        sleep_time = options.get("sleep_time")
        current_site = Site.objects.get_current()
        for url in urls_file.readlines():
            time.sleep(sleep_time)
            scheme, netloc, path, _, _, _ = urlparse(url.strip())
            _u = urlunparse(("http", current_site.domain, path, None, None, None))
            requests.get(_u)
            try:
                r = requests.get(_u)
                assert r.status_code == 200
            except AssertionError:
                self.stdout.write(
                    self.style.ERROR(
                        "Unable to access: {url} - "
                        "response code: {code}".format(url=_u, code=r.status_code)
                    )
                )
