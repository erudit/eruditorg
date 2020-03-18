# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import LegacyAccountProfile


class LegacyAccountProfileAdmin(admin.ModelAdmin):
    search_fields = ('id', 'user__first_name', 'user__last_name', 'user__email', )
    list_filter = ('user__is_active', 'origin', )
    list_display = (
        '_email',
        '_first_name',
        '_last_name',
        '_origin'
    )

    def _origin(self, obj):
        for origin in LegacyAccountProfile.ORIGIN_CHOICES:
            if origin[0] == obj.origin:
                return origin[1]

    def _email(self, obj):
        return obj.user.email
    short_description = _('Courriel')

    def _first_name(self, obj):
        return obj.user.first_name
    short_description = _('Prénom')

    def _last_name(self, obj):
        return obj.user.first_name
    short_description = _('Nom')


admin.site.register(LegacyAccountProfile, LegacyAccountProfileAdmin)
