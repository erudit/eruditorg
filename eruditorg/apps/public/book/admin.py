from django.contrib import admin
from .models import Book, BookCollection


class BookAdmin(admin.ModelAdmin):
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
    ]

admin.site.register(BookCollection)
admin.site.register(Book, BookAdmin)
