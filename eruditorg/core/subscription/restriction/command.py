# -*- coding: utf-8 -*-
import os.path as op

from django.core.management.base import BaseCommand
from PIL import Image

from .conf import settings as restriction_settings
from .models import Abonne


class ImportException(Exception):
    pass


class Command(BaseCommand):
    args = "<action:check_ongoing_restrictions|gen_dummy_badges>"
    help = 'Import data from the "restriction" database'

    def handle(self, *args, **options):
        if len(args) == 0:
            self.stdout.write(self.args)
            return

        self.args = args
        command = args[0]
        self.stdout.write(command)
        cmd = getattr(self, command)
        cmd()

    def gen_dummy_badges(self):
        for abonne in Abonne.objects.all():
            if not abonne.icone:
                continue
            im = Image.frombytes("L", (100, 100), b"\x00" * 100 * 100)
            im.save(op.join(restriction_settings.ABONNE_ICONS_PATH, abonne.icone))
