# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import AbonnementProfile


class AbonnementProfileAdmin(admin.ModelAdmin):
    search_fields = ('id', 'user__first_name', 'user__last_name', 'user__email', )
    list_filter = ('user__is_active', )
    list_display = (
        '_email',
        '_first_name',
        '_last_name',
    )

    def _email(self, obj):
        return obj.user.email
    short_description = _('Courriel')

    def _first_name(self, obj):
        return obj.user.first_name
    short_description = _('Prénom')

    def _last_name(self, obj):
        return obj.user.first_name
    short_description = _('Nom')


admin.site.register(AbonnementProfile, AbonnementProfileAdmin)
