# -*- coding: utf-8 -*-

from django.contrib import admin

from ..models import JournalProduction
from ..models import ProductionCenter
from ..models import ProductionType


admin.site.register(JournalProduction)
admin.site.register(ProductionCenter)
admin.site.register(ProductionType)
