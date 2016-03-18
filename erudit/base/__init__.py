# -*- coding: utf-8 -*-

default_app_config = 'base.apps.BaseConfig'


from .celery import app as celery_app  # noqa
