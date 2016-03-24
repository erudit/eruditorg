# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import AccountActionToken


class AccountActionTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'key', 'email', 'first_name', 'last_name', )
    list_display_links = ('id', 'key', 'email', )


admin.site.register(AccountActionToken, AccountActionTokenAdmin)
