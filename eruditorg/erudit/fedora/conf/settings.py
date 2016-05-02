# -*- coding: utf-8 -*-

from django.conf import settings


FEDORA_ROOT = getattr(settings, 'FEDORA_ROOT', 'http://localhost:8080/fedora/')
FEDORA_USER = getattr(settings, 'FEDORA_USER', 'fedoraAdmin')
FEDORA_PASSWORD = getattr(settings, 'FEDORA_PASSWORD', 'fedoraAdmin')

PIDSPACE = getattr(settings, 'ERUDIT_PIDSPACE', 'erudit')
