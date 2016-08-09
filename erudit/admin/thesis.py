# -*- coding: utf-8 -*-

from django.contrib import admin

from ..models import Thesis


class ThesisAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'author', 'url', )
    list_display_links = ('__str__', 'author', )


admin.site.register(Thesis, ThesisAdmin)
