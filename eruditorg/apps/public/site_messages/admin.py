from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import SiteMessage, TargetSite


class SiteMessageAdmin(TranslationAdmin):
    pass


admin.site.register(SiteMessage, SiteMessageAdmin)
admin.site.register(TargetSite)
