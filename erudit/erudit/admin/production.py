from django.contrib import admin

from erudit.models import (
    ProductionCenter,
    ProductionType,
    JournalProduction,
)

admin.site.register(ProductionCenter)
admin.site.register(ProductionType)
admin.site.register(JournalProduction)
