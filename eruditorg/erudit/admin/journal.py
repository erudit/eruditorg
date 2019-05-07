from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext as _
from django import forms

from ..models import Issue
from ..models import Journal
from ..models import JournalInformation
from ..models import JournalType


class JournalDisciplineInline(admin.TabularInline):
    model = Journal.disciplines.through


class JournalForm(forms.ModelForm):
    fields = 'all'
    model = Journal

    def clean(self):
        # In Django < 2.0, CharField stores empty values as empty strings, causing
        # a unicity constraint error when multiple objects have an empty value for
        # the same field. When we upgrade to Django 2.0, it will not be necessary
        # to convert empty strings to None values.
        if self.cleaned_data['localidentifier'] == "":
            self.cleaned_data['localidentifier'] = None
        return self.cleaned_data


class JournalAdmin(admin.ModelAdmin):
    form = JournalForm
    search_fields = ('code', 'name', 'issn_print', 'issn_web', 'external_url', )
    list_display = ('__str__', 'code', 'type', 'open_access', 'external_url', 'active', )
    list_display_links = ('__str__', 'code', )
    list_filter = ('collection', 'type', 'paper', 'open_access', 'active', )
    filter_horizontal = ('members', )

    fieldsets = [
        ('Identification', {
            'fields': (
                ('collection', 'type',),
                ('code', 'localidentifier',),
                ('name', 'subtitle',),
                ('is_new',),
                ('previous_journal', 'next_journal', ),
                ('issn_print', 'issn_web', ),
                ('external_url', 'redirect_to_external_url'),
            ),
        }),
        (None, {
            'fields': (
                ('open_access', 'paper'),
                ('first_publication_year', 'last_publication_year'),
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

    inlines = (JournalDisciplineInline, )

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.author = request.user
            instance.save()
        formset.save_m2m()


class IssueAdmin(admin.ModelAdmin):
    list_display = (
        'journal', 'year', 'volume', 'number', 'title', 'localidentifier',
        'is_published', 'view_issue_on_site', )
    search_fields = ('id', 'localidentifier', )
    list_filter = (
        'is_published', 'journal__collection', 'journal__name',
    )
    actions = [
        'make_published', 'make_unpublished',
        'force_free_access_to_true', 'force_free_access_to_false',
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
                'journal_code': obj.journal.code,
                'issue_slug': obj.volume_slug, 'localidentifier': obj.localidentifier, }
        )
        if not obj.is_published and obj.journal.collection.is_main_collection:
            url = "{url}?ticket={ticket}".format(
                url=url,
                ticket=obj.prepublication_ticket
            )
        return format_html(
            '<a href={}>{}</a>', url, _("Voir sur le site")
        )
    view_issue_on_site.short_description = _("Voir le numéro sur le site")

    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields + ('is_published',)


class JournalInformationAdmin(TranslationAdmin):
    pass


class JournalTypeAdmin(TranslationAdmin):
    pass


admin.site.register(Journal, JournalAdmin)
admin.site.register(Issue, IssueAdmin)
admin.site.register(JournalInformation, JournalInformationAdmin)
admin.site.unregister(JournalType)
admin.site.register(JournalType, JournalTypeAdmin)
