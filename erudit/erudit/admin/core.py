from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from erudit.models import (
    Author,
    Organisation,
    Library,
    Journal,
    JournalInformation,
    JournalType,
    Issue,
    Article,
    Publisher,
    Collection,
)

from core.permissions.admin import RuleInline


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


class CollectionAdmin(admin.ModelAdmin):

    list_display = (
        'code', 'name',
    )

    fieldsets = [
        ('Collection', {
            'fields': (
                ('name', 'code',)
            )
        }),
        ('Identification', {
            'fields': (
                'edinum_id', 'synced_with_edinum', 'sync_date'
            ),
        }),
    ]


class IssueAdmin(admin.ModelAdmin):

    search_fields = [
        'id', 'localidentifier'
    ]

    list_display = (
        'journal', 'year', 'volume', 'number', 'title', 'localidentifier',
    )


class ArticleAdmin(admin.ModelAdmin):

    search_fields = [
        'id', 'title', 'localidentifier'
    ]

    list_display = (
        'issue', 'localidentifier', 'title'
    )

    list_filter = [
        'issue'
    ]


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
                ('name', 'display_name',),
                ('subtitle',),
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


class JournalInformationAdmin(TranslationAdmin):
    pass


admin.site.register(Author)
admin.site.register(Organisation)
admin.site.register(Library)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Journal, JournalAdmin)
admin.site.register(JournalType)
admin.site.register(Issue, IssueAdmin)
admin.site.register(Publisher)
admin.site.register(Collection, CollectionAdmin)
admin.site.register(JournalInformation, JournalInformationAdmin)
