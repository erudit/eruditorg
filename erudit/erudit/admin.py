from django.contrib import admin

from erudit.models import Library #, LibraryComment
from erudit.models import Journal, JournalComment
from erudit.models import Issue #, IssueComment
from erudit.models import Publisher #, PublisherComment

# abstracts

class CommonAdmin(admin.ModelAdmin):

    readonly_fields = ['user_created', 'user_modified', 'date_created', 'date_modified']

    fieldsets = [
        ('Système', {
            'classes': ('collapse',),
            'fields': (
                ('date_created', 'user_created',),
                ('date_modified', 'user_modified',),
            ),
        }),
    ]

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'user_created', None) is None:
            obj.user_created = request.user
        obj.user_modified = request.user
        obj.save()


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


class JournalCommentInline(admin.TabularInline):
    model = JournalComment

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

#    def save_model(self, request, obj, form, change):
#        obj.author = request.user
#        obj.save()

class JournalAdmin(CommonAdmin):

    search_fields = ['code', 'name', 'display_name', 'issn_print', 'issn_web', 'url', 'address',]

    list_display = ('__str__', 'code', 'type', 'open_access', 'url', 'active', 'date_modified')
    list_display_links = ('__str__', 'code')
    list_filter = ['publisher', 'type', 'paper', 'open_access', 'active']
    list_editable = ['type', 'active', ]

    inlines = [
        JournalCommentInline,
    ]

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
    fieldsets.extend(CommonAdmin.fieldsets)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.author = request.user
            instance.save()
        formset.save_m2m()

class JournalCommentAdmin(CommentAdmin):

    fieldsets = [
        (None, {
            'fields': (
              'journal',
            )
        }),
    ]
    fieldsets.extend(CommentAdmin.fieldsets)

admin.site.register(Library)
admin.site.register(Journal, JournalAdmin)
#admin.site.register(JournalComment, JournalCommentAdmin)
admin.site.register(Issue)
admin.site.register(Publisher)
