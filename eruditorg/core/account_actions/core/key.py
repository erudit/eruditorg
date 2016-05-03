# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import uuid


def gen_action_key():
    """ Returns an action key: a random UUID. """
    return uuid.uuid4().hex
