from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import IndividualAccount, OrganizationPolicy


class IndividualAccountAdmin(admin.ModelAdmin):
    pass


class IndividualAccountInline(admin.TabularInline):
    model = IndividualAccount


class OrganizationPolicyAdmin(admin.ModelAdmin):
    list_display = (
        'organization',
        'comment',
        'ratio',
        'date_activation',
        'date_modification',
        'date_creation',
    )
    filter_horizontal = ("access_journal", "access_basket")
    inlines = (IndividualAccountInline, )
    fieldsets = (
        (None, {'fields': ('organization', 'comment', 'max_accounts')}),
        (_("Droits d'accès"), {'fields': (
            'access_full', 'access_journal', 'access_basket', )}),
    )

    def ratio(self, obj):
            return "{} / {}".format(obj.total_accounts, obj.max_accounts)
    ratio.short_description = _("Ratio d'utilisation")

admin.site.register(IndividualAccount, IndividualAccountAdmin)
admin.site.register(OrganizationPolicy, OrganizationPolicyAdmin)

# from .legacy import admin as legacy_admin  # NOQA
