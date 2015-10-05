from django.contrib import admin
from subscription.models import (
    Client, Product, RenewalNotice, RenewalNoticeStatus
)

class ProductAdmin(admin.ModelAdmin):
    search_fields = ['title', 'description',]
    list_display = ['title', 'description', 'amount',]
    list_display_link = ['title',]
    list_editable = ['amount',]


class ClientAdmin(admin.ModelAdmin):
    pass
    search_fields = ['firstname', 'lastname', 'organisation', 'email', 'postal_code',]
    list_display = ['firstname', 'lastname', 'organisation', 'email',]
    list_display_link = ['firstname', 'lastname',]
    list_filter = ['organisation', 'city', 'province', 'country',]
    fieldsets = [
        ('Identification', {
            'fields': (
                ('firstname', 'lastname'),
                'organisation',
            )
        }),
        ('Coordonnées', {
            'fields': (
                'email',
                'civic',
                'street',
                ('city', 'province'),
                ('country', 'postal_code'),
            )
        }),
    ]


def _country(obj):
    output = ""
    if obj and obj.paying_customer:
        output = "{:s}".format(
            obj.paying_customer.country,
        )
    return output
_country.short_description = 'Pays'


class RenewealNoticeAdmin(admin.ModelAdmin):
    search_fields = [
        'renewal_number',
        'po_number',
        'paying_customer__organisation',
        'receiving_customer__organisation',
        'paying_customer__lastname',
        'paying_customer__firstname',
        'receiving_customer__lastname',
        'receiving_customer__firstname',
        'comment',
        'paying_customer__country',
    ]

    list_display = [
        'renewal_number',
        'paying_customer',
        'receiving_customer',
        #'has_basket',
        #'has_rebate',
        'net_amount',
        'currency',
        'status',
        _country,
    ]
    list_display_link = ['renewal_number', ]
    list_filter = ['currency', 'status', 'rebate', 
        'paying_customer__country',
        #'has_basket',
        #'has_rebate',
    ]
    list_editable = ['status',]
    filter_horizontal = ('products',)
    readonly_fields = ['sent_emails', 
        #'has_basket',
    ]
    fieldsets = [
        ('Identification', {
            'fields': (
                ('renewal_number', 'po_number'),
                ('paying_customer', 'receiving_customer'),
            )
        }),
        ('Montants', {
            'fields': (
                'currency',
                ('amount_total', 'rebate'),
                ('raw_amount',),
                ('federal_tax',),
                ('provincial_tax',),
                ('harmonized_tax',),
                ('net_amount',),
            )
        }),
        ('Produits', {
            'fields': (
                'products',
            )
        }),
        ('Envois', {
            'fields': (
                'sent_emails',
            )
        }),
        ('Suivi', {
            'fields': (
                ('status', 'date_created', ),
                'comment',
            )
        }),
    ]


# Register your models here.
admin.site.register(Product, ProductAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(RenewalNotice, RenewealNoticeAdmin)
admin.site.register(RenewalNoticeStatus)
