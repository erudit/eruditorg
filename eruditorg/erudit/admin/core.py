from django.contrib import admin

from ..models import Collection
from ..models import JournalType
from ..models import Organisation
from ..models import Language


class CollectionAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
    )
    fieldsets = [
        (
            "Identification",
            {
                "fields": (
                    (
                        "name",
                        "is_main_collection",
                    ),
                    (
                        "code",
                        "localidentifier",
                    ),
                    ("logo",),
                )
            },
        ),
    ]


class OrganisationAdmin(admin.ModelAdmin):
    search_fields = ("name",)

    filter_horizontal = ("members",)


admin.site.register(Organisation, OrganisationAdmin)
admin.site.register(JournalType)
admin.site.register(Language)
admin.site.register(Collection, CollectionAdmin)
