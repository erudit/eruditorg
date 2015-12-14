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


class JournalAdmin(admin.ModelAdmin):

    search_fields = [
        'code', 'name', 'display_name', 'issn_print',
        'issn_web', 'url', 'address',
    ]

    list_display = (
        '__str__', 'code', 'type', 'open_access',
        'url', 'active',
    )

    list_display_links = ('__str__', 'code')

    list_filter = [
        'publisher', 'type', 'paper', 'open_access', 'active'
    ]

    list_editable = ['type', 'active', ]

    fieldsets = [
        ('Identification', {
            'fields': (
                ('code', 'formerly'),
                ('name', 'display_name'),
                ('issn_print', 'issn_web'),
            ),
        }),
        (None, {
            'fields': (
                ('publisher', 'type'),
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
