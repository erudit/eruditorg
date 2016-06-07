# -*- coding: utf-8 -*-

from django.contrib import admin

from ..models import Contract
from ..models import ContractStatus
from ..models import ContractType


class ContractAdmin(admin.ModelAdmin):
    search_fields = ['journal__name', 'journal__code', 'type__code', ]
    list_display = (
        '__str__',
        'journal',
        'type',
        'date_start',
        'date_end',
        'date_signature',
        'status',
    )
    list_display_link = ('__str__',)
    list_filter = ['type', 'status', 'journal', ]
    list_editable = ['date_start', 'date_end', ]

    fieldsets = [
        ('Identification', {
            'fields': (
                'journal',
                'type',
            )
        }),
        ('Dates', {
            'fields': (
                ('date_start', 'date_end'),
            )
        }),
        ('Signature', {
            'classes': ('collapse',),
            'fields': (
                ('date_signature', ),
            )
        }),
        ('État', {
            'classes': ('collapse',),
            'fields': (
                'status',
            ),
        }),
    ]


class ContractTypeAdmin(admin.ModelAdmin):
    pass


class ContractStatusAdmin(admin.ModelAdmin):
    pass


admin.site.register(Contract, ContractAdmin)
admin.site.register(ContractType, ContractTypeAdmin)
admin.site.register(ContractStatus, ContractStatusAdmin)
