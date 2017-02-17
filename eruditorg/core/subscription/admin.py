# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import InstitutionIPAddressRange
from .models import InstitutionReferer
from .models import JournalAccessSubscription
from .models import JournalAccessSubscriptionPeriod
from .models import JournalManagementPlan
from .models import JournalManagementSubscription
from .models import JournalManagementSubscriptionPeriod


class JournalAccessSubscriptionPeriodInline(admin.TabularInline):
    model = JournalAccessSubscriptionPeriod


class InstitutionRefererInline(admin.TabularInline):
    model = InstitutionReferer


class InstitutionIPAddressRangeAdmin(admin.ModelAdmin):
    search_fields = ('subscription__organisation__name',)


class JournalAccessSubscriptionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {
            'fields': ('title', 'comment', 'sponsor', ),
        }),
        (_('Bénéficiaire'), {
            'fields': ('user', 'organisation', ),
        }),
        (_('Revue(s) cibles'), {
            'fields': ('journal', 'journals', 'collection', 'full_access', ),
        }),
    ]

    search_fields = ('organisation__name',)
    inlines = [JournalAccessSubscriptionPeriodInline, InstitutionRefererInline]

    list_display = ('pk', 'title', 'user', 'organisation', 'journal', 'collection', 'full_access', )
    list_display_links = ('pk', 'title', 'user', 'organisation', )


class JournalManagementPlanAdmin(admin.ModelAdmin):
    list_display = ('pk', 'code', 'title', )
    list_display_links = ('pk', 'code', )


class JournalManagementSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'journal', 'plan', )
    list_display_links = ('pk', 'title', 'journal', )


admin.site.register(InstitutionIPAddressRange, InstitutionIPAddressRangeAdmin)
admin.site.register(JournalAccessSubscription, JournalAccessSubscriptionAdmin)
admin.site.register(JournalAccessSubscriptionPeriod)
admin.site.register(JournalManagementPlan, JournalManagementPlanAdmin)
admin.site.register(JournalManagementSubscription, JournalManagementSubscriptionAdmin)
admin.site.register(JournalManagementSubscriptionPeriod)
