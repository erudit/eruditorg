from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType

from .models import IndividualAccount, OrganizationPolicy


class IndividualAccountAdmin(admin.ModelAdmin):
    list_filter = ('organization_policy', )
    list_display = (
        'id',
        'firstname',
        'lastname',
        'email',
        'organization_policy',
    )


class OrganizationPolicyAdmin(admin.ModelAdmin):
    list_display = (
        'organization',
        'comment',
        'ratio',
        'date_activation',
        'date_renew',
        'date_modification',
        'date_creation',

    )
    filter_horizontal = ("access_journal", "access_basket")
    fieldsets = (
        (None, {'fields': (
            'organization',
            'comment',
            'max_accounts',
            'renew_cycle',
            'date_activation',
        )}),
        (_("Droits d'accès"), {'fields': (
            'access_full', 'access_journal', 'access_basket', )}),
    )
    actions = ['renew', ]

    def ratio(self, obj):
        if not obj.max_accounts:
            maxi = "~"
        else:
            maxi = obj.max_accounts
        return "{} / {}".format(obj.total_accounts, maxi)
    ratio.short_description = _("Ratio d'utilisation")

    def renew(self, request, queryset):
        for obj in queryset:
            obj.renew()
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(obj).pk,
                object_id=obj.pk,
                object_repr=str(obj),
                action_flag=CHANGE,
                change_message=_("Renouvellement jusqu'à %s (%s jours)" % (obj.date_renew, obj.renew_cycle)),
            )
            self.message_user(request, "%s a été renouvellée jusqu'à %s." % (obj, obj.date_renew))
    renew.short_description = _("Renouveller l'inscription")

admin.site.register(IndividualAccount, IndividualAccountAdmin)
admin.site.register(OrganizationPolicy, OrganizationPolicyAdmin)
