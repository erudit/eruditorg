# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import imp

from django.conf import settings
from django.utils.importlib import import_module


def load(modname):
    """ Loads all the modules that are named 'modname' from all the installed applications. """

    def _get_module(app, modname):
        # Find out the app's __path__
        try:
            app_path = import_module(app).__path__
        except AttributeError:  # pragma: no cover
            return

        # Use imp.find_module to find the app's modname.py
        try:
            imp.find_module(modname, app_path)
        except ImportError:  # pragma: no cover
            return

        # Import the app's module file
        import_module('{}.{}'.format(app, modname))

    for app in settings.INSTALLED_APPS:
        _get_module(app, modname)
