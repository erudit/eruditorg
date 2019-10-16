from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import Campaign


class CampaignAdmin(TranslationAdmin):
    list_display = ("__str__", "url", "image", "active")


admin.site.register(Campaign, CampaignAdmin)
