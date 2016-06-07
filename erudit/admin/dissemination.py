# -*- coding: utf-8 -*-

from django.contrib import admin

from ..models import Indexation
from ..models import Indexer


admin.site.register(Indexation)
admin.site.register(Indexer)
