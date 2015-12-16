from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import IndividualAccount, Organization


class IndividualAccountAdmin(admin.ModelAdmin):
    pass


class IndividualAccountInline(admin.TabularInline):
    model = IndividualAccount


class OrganizationAdmin(admin.ModelAdmin):
    filter_horizontal = ("access_journal", )
    inlines = (IndividualAccountInline, )
    fieldsets = (
        (None, {'fields': ('name', 'max_accounts')}),
        (_("Droits d'accès"), {'fields': ('access_full', 'access_journal', )}),
    )

admin.site.register(IndividualAccount, IndividualAccountAdmin)
admin.site.register(Organization, OrganizationAdmin)

# from .legacy import admin as legacy_admin  # NOQA
