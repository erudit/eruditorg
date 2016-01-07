from django.contrib import admin
from django.utils.translation import gettext as _
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from subscription.models import (
    Client, Product, RenewalNotice,
    Country, Currency
)


class CountryAdmin(admin.ModelAdmin):
    search_fields = (
        'code',
        'name',
        'currency__code',
    )
    list_display = (
        'code',
        'name',
        'currency',
    )
    list_display_link = (
        'name',
    )
    list_editable = (
        'code',
        'currency',
    )


class CurrencyAdmin(admin.ModelAdmin):
    search_fields = (
        'code',
        'name',
    )
    list_display = (
        'code',
        'name',
    )
    list_display_link = (
        'code',
    )
    list_editable = (
        'name',
    )


class ProductAdmin(admin.ModelAdmin):
    search_fields = (
        'title',
        'description',
    )
    list_display = (
        'title',
        'description',
        'amount',
        'hide_in_renewal_items'
    )
    list_display_link = (
        'title',
    )
    list_editable = (
        'amount',
    )

    filter_horizontal = (
        'titles',
    )


class ClientAdmin(admin.ModelAdmin):
    search_fields = (
        'firstname',
        'lastname',
        'organisation',
        'email',
        'postal_code',
    )
    list_display = (
        'firstname',
        'lastname',
        'organisation',
        'email',
        'country',
        'currency',
        'exemption_code',
    )
    list_display_links = (
        'firstname',
        'lastname',
        'organisation',
    )
    list_filter = (
        'organisation',
        'city',
        'province',
        'country',
    )

    fieldsets = (
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
                'pobox',
                ('city', 'province'),
                ('country', 'postal_code'),
            )
        }),
        ('Finance', {
            'fields': (
                'exemption_code',
                'currency',
            )
        }),
    )


def _country(obj):
    output = ""
    if obj and obj.paying_customer:
        output = "{:s}".format(
            obj.paying_customer.country,
        )
    return output
_country.short_description = 'Pays'


class RenewalNoticeAdmin(admin.ModelAdmin):
    search_fields = (
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
    )

    list_display = (
        'renewal_number',
        'paying_customer',
        'receiving_customer',
        'has_basket',
        'has_rebate',
        'rebate',
        'net_amount',
        'currency',
        _country,
        'is_correct',
        'status',
        'has_been_answered',
        'has_renewed',
        'is_paid',
        'has_refused',
    )

    list_display_link = (
        'renewal_number',
    )

    list_filter = (
        'currency',
        'status',
        'rebate',
        'paying_customer__country',
        'has_basket',
        'has_rebate',
        'is_correct',
        'has_been_answered',
        'has_renewed',
        'has_refused',
    )

    def flag_dont_send(modeladmin, request, queryset):
        queryset.update(status='DONT')

    flag_dont_send.short_description = _("Marquer comme « Ne pas envoyer »")

    def flag_send(modeladmin, request, queryset):
        queryset.update(status='TODO')

    flag_send.short_description = _("Marquer comme « À envoyer »")

    def create_test_email(modeladmin, request, queryset):
        """ Create a renewal email for this RenewalNotice """
        selected = [str(r.pk) for r in queryset.all()]

        if len(selected) > 0:
            url = reverse('confirm_test')

            return HttpResponseRedirect("{}?ids={}".format(
                url,
                ",".join(selected))
            )

    create_test_email.short_description = _("Envoyer un courriel de test")

    def create_email(modeladmin, request, queryset):
        """ Create a renewal email for this RenewalNotice """
        selected = [str(r.pk) for r in queryset.filter(
            status__in=('TODO', 'REDO',)
        )]

        if len(selected) > 0:
            url = reverse('confirm_send')

            return HttpResponseRedirect("{}?ids={}".format(
                url,
                ",".join(selected))
            )

    create_email.short_description = _("Envoyer le courriel")

    list_editable = (
        'status',
        'has_rebate',
    )
    filter_horizontal = (
        'products',
    )
    readonly_fields = (
        'sent_emails',
        'is_correct',
        'error_msg',
    )

    fieldsets = (
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
                ('status', 'date_created'),
                ('has_been_answered', 'is_paid', 'has_renewed', 'has_refused'),
                'comment',
                'is_correct',
                'error_msg',
            )
        }),
    )

    actions = [create_test_email, flag_dont_send, flag_send, create_email]

# Register your models here.
admin.site.register(Product, ProductAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(RenewalNotice, RenewalNoticeAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Currency, CurrencyAdmin)
