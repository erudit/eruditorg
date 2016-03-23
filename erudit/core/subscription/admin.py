# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import InstitutionIPAddressRange
from .models import JournalAccessSubscription
from .models import JournalManagementPlan
from .models import JournalManagementSubscription


class JournalAccessSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'user', 'organisation', 'journal', 'collection', 'full_access', )
    list_display_links = ('pk', 'title', 'user', 'organisation', )


class JournalManagementPlanAdmin(admin.ModelAdmin):
    list_display = ('pk', 'code', 'title', )
    list_display_links = ('pk', 'code', )


class JournalManagementSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'journal', 'plan', )
    list_display_links = ('pk', 'title', 'journal', )


admin.site.register(InstitutionIPAddressRange)
admin.site.register(JournalAccessSubscription, JournalAccessSubscriptionAdmin)
admin.site.register(JournalManagementPlan, JournalManagementPlanAdmin)
admin.site.register(JournalManagementSubscription, JournalManagementSubscriptionAdmin)
