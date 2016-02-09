# -*- coding: utf-8 -*-

from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import JournalInformation


class JournalInformationAdmin(TranslationAdmin):
    pass


admin.site.register(JournalInformation, JournalInformationAdmin)
