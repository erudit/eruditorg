# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.translation import gettext as _

from ..models import Thesis


class ThesisAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'author', 'url', )
    list_display_links = ('__str__', 'author', )

    search_fields = ('author__lastname', 'title',)

    fieldsets = (
        (('Identification du document'), {
            'fields': (
                ('title', 'author',),
                ('collection', 'url'),
            ),
        }),
        (_('Information système'), {
            'fields': (
                ('oai_datestamp',),
            )
        }),
    )


admin.site.register(Thesis, ThesisAdmin)
