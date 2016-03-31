# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import AccountActionToken


class AccountActionTokenAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'key', 'email', 'first_name', 'last_name', 'action', 'active', 'expiration_date',
        'is_expired', 'is_consumed', )
    list_display_links = ('id', 'key', 'email', )


admin.site.register(AccountActionToken, AccountActionTokenAdmin)
