from django.contrib import admin

from erudit.models import (
    Person,
    Organisation,
    Library,
    Journal,
    JournalType,
    Issue,
    Publisher,
)

from permissions.admin import RuleInline


class CommentAdmin(admin.ModelAdmin):

    readonly_fields = ['author', 'date']

    fieldsets = [
        (None, {
            'fields': (
                ('date', 'author',),
            )
        }),
        (None, {
            'fields': (
                'comment',
            )
        }),
    ]

    def save_model(self, request, obj, form, change):
        obj.author = request.user
        obj.save()


class JournalRuleInline(RuleInline):
    permission_filters = (
        'userspace.manage_permissions',
        'editor.manage_journal',
    )


class JournalAdmin(admin.ModelAdmin):
    inlines = (JournalRuleInline, )

    search_fields = [
        'code', 'name', 'display_name', 'issn_print',
        'issn_web', 'url', 'address', 'members'
    ]

    list_display = (
        '__str__', 'code', 'type', 'open_access',
        'url', 'active',
    )

    list_display_links = ('__str__', 'code')

    list_filter = [
        'publishers', 'type', 'paper', 'open_access', 'active'
    ]

    filter_horizontal = (
        'members',
        'publishers',
    )

    list_editable = ['type', 'active', ]

    fieldsets = [
        ('Identification', {
            'fields': (
                ('code', 'formerly'),
                ('localidentifier',),
                ('name', 'display_name'),
                ('issn_print', 'issn_web'),
            ),
        }),
        (None, {
            'fields': (
                ('publishers',),
                ('type'),
            ),
        }),
        (None, {
            'fields': (
                ('open_access', 'paper'),
                'issues_per_year',
            ),
        }),
        ('Contacts', {
            'classes': ('collapse',),
            'fields': (

            ),
        }),
        ('Coordonnées', {
            'classes': ('collapse',),
            'fields': (
                'url',
                'address',
            ),
        }),
        ('Membres', {
            'fields': (
                'members',
            )
        }),
        ('État', {
            'classes': ('collapse',),
            'fields': (
                'active',
            ),
        }),
    ]

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.author = request.user
            instance.save()
        formset.save_m2m()


admin.site.register(Person)
admin.site.register(Organisation)
admin.site.register(Library)
admin.site.register(Journal, JournalAdmin)
admin.site.register(JournalType)
admin.site.register(Issue)
admin.site.register(Publisher)
