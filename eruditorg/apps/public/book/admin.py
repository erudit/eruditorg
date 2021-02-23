import csv

from datetime import datetime
from django.contrib import admin
from django.http import HttpResponse
from django.utils.translation import gettext as _

from .models import Book, BookCollection


class BookAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "year",
        "authors",
        "collection",
        "slug",
        "publisher",
        "isbn",
        "digital_isbn",
        "is_published",
    )
    list_filter = (
        "collection",
        "is_open_access",
        "is_published",
    )

    fieldsets = [
        (None, {"fields": (("type", "collection", "parent_book"),)}),
        (None, {"fields": (("title", "subtitle", "slug"),)}),
        (None, {"fields": (("year",),)}),
        (
            None,
            {
                "fields": (
                    (
                        "publisher",
                        "publisher_url",
                    ),
                )
            },
        ),
        (
            None,
            {
                "fields": (
                    (
                        "authors",
                        "contribution",
                    ),
                )
            },
        ),
        (
            None,
            {
                "fields": (
                    (
                        "isbn",
                        "digital_isbn",
                    ),
                )
            },
        ),
        (None, {"fields": (("cover",),)}),
        (None, {"fields": (("copyright",),)}),
        (None, {"fields": (("is_open_access", "is_published"),)}),
        (None, {"fields": (("path",),)}),
    ]

    actions = ["mark_as_oa", "remove_cover", "export_as_csv"]

    def mark_as_oa(self, request, queryset):
        queryset.update(is_open_access=True)

    mark_as_oa.short_description = _("Afficher en libre accès")

    def remove_cover(self, request, queryset):
        queryset.update(cover=None)

    remove_cover.short_description = _("Supprimer les couvertures")

    def export_as_csv(self, request, queryset):
        field_labels = {field.name: field.verbose_name for field in self.model._meta.fields}
        fields = [
            "title",
            "subtitle",
            "type",
            "year",
            "authors",
            "collection",
            "slug",
            "publisher",
            "isbn",
            "digital_isbn",
            "is_published",
            "is_open_access",
        ]

        response = HttpResponse(content_type="text/csv")
        date = datetime.now().strftime("%Y-%m-%d")
        response["Content-Disposition"] = f'attachment; filename="livres-{date}.csv"'
        writer = csv.writer(response)
        writer.writerow([field_labels.get(field) for field in fields])

        def get_field_value(obj, field):
            value_map = {
                True: _("Oui"),
                False: _("Non"),
                "li": _("Livre"),
                "ac": _("Actes"),
            }
            value = getattr(obj, field)
            return value_map.get(value, value)

        for obj in queryset:
            writer.writerow(get_field_value(obj, field) for field in fields)

        return response

    export_as_csv.short_description = _("Exporter les livres en CSV")


admin.site.register(BookCollection)
admin.site.register(Book, BookAdmin)
