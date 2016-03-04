# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import Authorization


class AuthorizationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'group',
        'authorization_codename',
        'content_type',
        '_content_object',
        'date_modification',
        'date_creation',

    )
    list_filter = ('content_type', )

    def _content_object(self, obj):
        if not obj.content_object:
            return
        else:
            return str(obj.content_object)

    _content_object.short_description = _('Objet')
    _content_object.allow_tags = True


admin.site.register(Authorization, AuthorizationAdmin)
