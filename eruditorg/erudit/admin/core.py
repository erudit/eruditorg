from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from ..models import Collection
from ..models import Discipline
from ..models import JournalType
from ..models import Organisation
from ..models import LegacyOrganisationProfile
from ..models import Language


class CollectionAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', )
    fieldsets = [
        ('Identification', {
            'fields': (
                ('name', 'is_main_collection',),
                ('code', 'localidentifier',),
                ('logo', ),
            )
        }),
    ]


class DisciplineAdmin(TranslationAdmin):
    pass


class LegacyOrganisationProfileInline(admin.TabularInline):
    model = LegacyOrganisationProfile


class OrganisationAdmin(admin.ModelAdmin):
    search_fields = ('name',)

    inlines = (LegacyOrganisationProfileInline, )

    filter_horizontal = ('members',)


admin.site.register(Organisation, OrganisationAdmin)
admin.site.register(JournalType)
admin.site.register(Language)
admin.site.register(Collection, CollectionAdmin)
admin.site.register(Discipline, DisciplineAdmin)
