from django.contrib import admin
from .models import Book, BookCollection
from django.utils.translation import gettext as _


class BookAdmin(admin.ModelAdmin):

    list_display = ('title', 'year', 'authors', 'collection',)
    list_filter = ('collection', 'is_open_access',)

    fieldsets = [
        (None, {
            'fields': (
                ('type', 'collection',),
            )
        }),
        (None, {
            'fields': (
                ('title', 'subtitle',),
            )
        }),
        (None, {
            'fields': (
                ('year',),
            )
        }),
        (None, {
            'fields': (
                ('publisher', 'publisher_url',),
            )
        }),
        (None, {
            'fields': (
                ('authors', 'contribution',),
            )
        }),
        (None, {
            'fields': (
                ('isbn', 'digital_isbn',),
            )
        }),
        (None, {
            'fields': (
                ('cover',),
            )
        }),
        (None, {
            'fields': (
                ('copyright',),
            )
        }),
        (None, {
            'fields': (
                ('is_open_access',),
            )
        }),
    ]

    actions = [
        'mark_as_oa',
    ]

    def mark_as_oa(self, request, queryset):
        queryset.update(is_open_access=True)
    mark_as_oa.short_description = _('Afficher en libre accès')


admin.site.register(BookCollection)
admin.site.register(Book, BookAdmin)
