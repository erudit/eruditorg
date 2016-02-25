from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.admin import GenericStackedInline
from django.core.urlresolvers import reverse

from .models import (IndividualAccount, Policy, PolicyEvent,
                     Organisation, Journal, InstitutionalAccount,
                     InstitutionIPAddressRange)


class PolicyEventAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'date_creation',
        'policy',
        'code',
        'message',
    )
    search_fields = ('message', 'code', )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, pk=None):
        return request.user.is_superuser


class PolicyInline(GenericStackedInline):
    """
    Policy can be created in Django admin from IndividualAccount or Organization.
    (Note : if you create a policy from IndividualAccount, this one will be
    automatically set to the account policy property, so you don't have to select
    anything in this case.)
    """
    model = Policy
    max_num = 1
    filter_horizontal = ("managers", "access_journal", )
    fieldsets = (
        (None, {'fields': (
            'comment',
            'max_accounts',
            'renew_cycle',
            'date_activation',
        )}),
        (_("Droits d'accès"), {'fields': (
            'access_full', 'access_journal', )}),
    )


class IndividualAccountAdmin(admin.ModelAdmin):
    inlines = (PolicyInline, )
    search_fields = ('id', 'firstname', 'lastname', 'email', )
    list_filter = ('policy', 'active', )
    list_display = (
        'id',
        'firstname',
        'lastname',
        'email',
        'policy',
        'active',
    )

    def save_formset(self, request, form, formset, change):
        super(IndividualAccountAdmin, self).save_formset(request, form, formset, change)
        policies = [instance for instance in formset.save(commit=False) if
                    instance.__class__ == Policy]
        if len(policies) > 1:
            raise Exception(_("Une seule règle d'accès ne peut être gérée pour l'instant"))
        if len(policies) == 1:
            form.instance.policy = policies[0]
            form.instance.save()


class OrganisationAdmin(admin.ModelAdmin):
    inlines = (PolicyInline, )
    fields = ('name', )
    readonly_fields = ('name', )

    def has_add_permission(self, request):
        """
        Only provide policy settings for existing Organizations.
        """
        return False

    def has_delete_permission(self, request, pk=None):
        """
        Only provide policy settings for existing Organizations.
        """
        return False


class JournalAdmin(admin.ModelAdmin):
    inlines = (PolicyInline, )
    fields = ('name', )
    readonly_fields = ('name', )

    def has_add_permission(self, request):
        """
        Only provide policy settings for existing Journal.
        """
        return False

    def has_delete_permission(self, request, pk=None):
        """
        Only provide policy settings for existing Journal.
        """
        return False


class PolicyAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'content_type',
        '_content_object',
        'comment',
        'ratio',
        'date_activation',
        'renew_cycle',
        'date_renew',
        'date_modification',
        'date_creation',

    )
    list_filter = ('content_type', )
    filter_horizontal = ("managers", "access_journal", )
    fieldsets = (
        (None, {'fields': (
            'managers',
            'max_accounts',
            'renew_cycle',
            'date_activation',
        )}),
        (_("Droits d'accès"), {'fields': (
            'access_full', 'access_journal', )}),
    )
    actions = ['renew', ]

    def has_add_permission(self, request):
        """
        Content type / object can't be selected
        """
        return False

    def ratio(self, obj):
        if not obj.max_accounts:
            maxi = "~"
        else:
            maxi = obj.max_accounts
        return "{} / {}".format(obj.total_accounts, maxi)
    ratio.short_description = _("Ratio d'utilisation")

    def _content_object(self, obj):
        """
        Link is hardcoded to the proxy model overriden in this app!
        """
        if not obj.content_object:
            return
        url = reverse("admin:subscription_{}_change".format(
            obj.content_object.__class__.__name__.lower()),
            args=(obj.content_object.id, ))
        return "<a href='{}'>{}</a>".format(url, obj.content_object)
    _content_object.short_description = _("Objet")
    _content_object.allow_tags = True

    def renew(self, request, queryset):
        for obj in queryset:
            obj.renew()
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(obj).pk,
                object_id=obj.pk,
                object_repr=str(obj),
                action_flag=CHANGE,
                change_message=_("Renouvellement jusqu'à %s (%s jours)" % (
                    obj.date_renew, obj.renew_cycle)),
            )
            self.message_user(request, "%s a été renouvellée jusqu'à %s." % (obj, obj.date_renew))
    renew.short_description = _("Renouveller l'inscription")


admin.site.register(IndividualAccount, IndividualAccountAdmin)
admin.site.register(Policy, PolicyAdmin)
admin.site.register(Organisation, OrganisationAdmin)
admin.site.register(Journal, JournalAdmin)
admin.site.register(PolicyEvent, PolicyEventAdmin)
admin.site.register(InstitutionalAccount)
admin.site.register(InstitutionIPAddressRange)
