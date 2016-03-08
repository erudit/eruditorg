# -*- coding: utf-8 -*-

import contextlib

from django.utils import translation


@contextlib.contextmanager
def switch_language(language):
    """ A context manager to easily switch to another language. """
    current_lang = translation.get_language()
    translation.activate(language)
    yield
    translation.activate(current_lang)
