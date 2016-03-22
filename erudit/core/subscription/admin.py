# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import InstitutionalAccount
from .models import InstitutionIPAddressRange


class JournalAdmin(admin.ModelAdmin):
    fields = ('name', )
    readonly_fields = ('name', )

    def has_add_permission(self, request):
        """
        Only provide policy settings for existing Journal.
        """
        return False

    def has_delete_permission(self, request, pk=None):
        """
        Only provide policy settings for existing Journal.
        """
        return False


admin.site.register(InstitutionalAccount)
admin.site.register(InstitutionIPAddressRange)
