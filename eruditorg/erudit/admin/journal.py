from django.contrib import admin
from django.contrib.admin.widgets import AdminIntegerFieldWidget
from django.core.validators import MaxValueValidator, MinValueValidator
from modeltranslation.admin import TranslationAdmin
from django.urls import reverse
from django.utils import timezone as tz
from django.utils.html import format_html
from django.utils.translation import gettext as _
from django import forms
from reversion_compare.admin import CompareVersionAdmin

from ..models import Issue
from ..models import Journal
from ..models import JournalInformation
from ..models import JournalType


JOURNAL_INFORMATION_COMPARE_EXCLUDE = [
    # Exclude the translated base fields (ie. about) because the translation fields (ie. about_fr)
    # are already displayed.
    "about",
    "contact",
    "editorial_policy",
    "instruction_for_authors",
    "partners",
    "publishing_ethics",
    "subscriptions",
    "team",
    # Exclude the auto_now date field.
    "updated",
]


class JournalDisciplineInline(admin.TabularInline):
    model = Journal.disciplines.through


class JournalForm(forms.ModelForm):
    fields = "all"
    model = Journal

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Limit `year_of_addition` field values to the current year and the next two years.
        now = tz.now()
        min_year = now.year
        max_year = min_year + 2
        self.fields["year_of_addition"].validators = [
            MinValueValidator(min_year),
            MaxValueValidator(max_year),
        ]
        self.fields["year_of_addition"].widget = AdminIntegerFieldWidget(
            attrs={
                "min": min_year,
                "max": max_year,
            },
        )

    def clean(self):
        # In Django < 2.0, CharField stores empty values as empty strings, causing
        # a unicity constraint error when multiple objects have an empty value for
        # the same field. When we upgrade to Django 2.0, it will not be necessary
        # to convert empty strings to None values.
        if self.cleaned_data["localidentifier"] == "":
            self.cleaned_data["localidentifier"] = None
        return self.cleaned_data


class JournalAdmin(admin.ModelAdmin):
    form = JournalForm
    search_fields = (
        "code",
        "name",
        "issn_print",
        "issn_web",
        "external_url",
    )
    list_display = (
        "__str__",
        "code",
        "type",
        "open_access",
        "external_url",
        "active",
    )
    list_display_links = (
        "__str__",
        "code",
    )
    list_filter = (
        "collection",
        "type",
        "paper",
        "open_access",
        "active",
        "is_new",
        "year_of_addition",
    )
    filter_horizontal = ("members",)

    fieldsets = [
        (
            "Identification",
            {
                "fields": (
                    (
                        "collection",
                        "type",
                    ),
                    (
                        "code",
                        "localidentifier",
                    ),
                    (
                        "name",
                        "subtitle",
                    ),
                    ("is_new", "year_of_addition"),
                    (
                        "previous_journal",
                        "next_journal",
                    ),
                    (
                        "issn_print",
                        "issn_web",
                    ),
                    ("external_url", "redirect_to_external_url"),
                ),
            },
        ),
        (
            None,
            {
                "fields": (
                    ("open_access", "charges_apc", "paper"),
                    ("first_publication_year", "last_publication_year"),
                ),
            },
        ),
        ("Membres", {"fields": ("members",)}),
        (
            "État",
            {
                "classes": ("collapse",),
                "fields": ("active",),
            },
        ),
    ]

    inlines = (JournalDisciplineInline,)


class IssueAdmin(admin.ModelAdmin):
    list_display = (
        "journal",
        "year",
        "volume",
        "number",
        "title",
        "localidentifier",
        "is_published",
        "view_issue_on_site",
    )
    search_fields = (
        "id",
        "localidentifier",
    )
    list_filter = (
        "is_published",
        "journal__collection",
        "journal__name",
    )
    actions = [
        "make_published",
        "make_unpublished",
        "force_free_access_to_true",
        "force_free_access_to_false",
    ]

    def force_free_access_to_true(self, request, queryset):
        """Mark a set of issues as open access"""
        queryset.update(force_free_access=True)

    force_free_access_to_true.short_description = _(
        "Contraindre les numéros sélectionnés en libre d'accès"
    )

    def force_free_access_to_false(self, request, queryset):
        """Mark a set of issues as not open access"""
        queryset.update(force_free_access=False)

    force_free_access_to_false.short_description = _(
        "Ne pas contraindre ces numéros au libre accès"
    )

    def view_issue_on_site(self, obj):
        """ Display the link leading to the issue on website """
        url = reverse(
            "public:journal:issue_detail",
            kwargs={
                "journal_code": obj.journal.code,
                "issue_slug": obj.volume_slug,
                "localidentifier": obj.localidentifier,
            },
        )
        if not obj.is_published and obj.journal.collection.is_main_collection:
            url = "{url}?ticket={ticket}".format(url=url, ticket=obj.prepublication_ticket)
        return format_html("<a href={}>{}</a>", url, _("Voir sur le site"))

    view_issue_on_site.short_description = _("Voir le numéro sur le site")

    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields + ("is_published",)


class JournalInformationAdmin(CompareVersionAdmin, TranslationAdmin):
    compare_exclude = JOURNAL_INFORMATION_COMPARE_EXCLUDE


class JournalTypeAdmin(TranslationAdmin):
    pass


admin.site.register(Journal, JournalAdmin)
admin.site.register(Issue, IssueAdmin)
admin.site.register(JournalInformation, JournalInformationAdmin)
admin.site.unregister(JournalType)
admin.site.register(JournalType, JournalTypeAdmin)
