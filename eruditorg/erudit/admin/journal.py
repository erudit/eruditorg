from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from django.db.models import Q
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext as _
from django import forms

from ..models import Article
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
    filter_horizontal = ('members', 'publishers', )

    fieldsets = [
        ('Identification', {
            'fields': (
                ('collection', 'type',),
                ('code', 'localidentifier',),
                ('name', 'subtitle',),
                ('is_new',),
                ('previous_journal', 'next_journal', ),
                ('issn_print', 'issn_web', ),
                ('website_url', ),
                ('external_url', 'redirect_to_external_url'),
            ),
        }),
        (None, {
            'fields': (
                ('publishers',),
            ),
        }),
        (None, {
            'fields': (
                ('open_access', 'paper'),
                ('issues_per_year', 'first_publication_year', 'last_publication_year'),
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
        'is_published', 'is_published_in_fedora', 'view_issue_on_site', )
    search_fields = ('id', 'localidentifier', )
    list_filter = (
        'is_published', 'journal__collection', 'journal__name',
    )
    actions = [
        'make_published', 'make_unpublished',
        'force_free_access_to_true', 'force_free_access_to_false',
    ]

    def is_published_in_fedora(self, obj):
        return obj.is_published_in_fedora()
    is_published_in_fedora.short_description = "Publié dans Fedora"

    def make_published(self, request, queryset):
        """Mark a set of issues as published"""
        queryset.update(is_published=True)
    make_published.short_description = _("Marquer les numéros sélectionnés comme diffusés")

    def make_unpublished(self, request, queryset):
        """Mark a set of issues as pre-published"""
        queryset.update(is_published=False)
    make_unpublished.short_description = _("Marquer les numéros sélectionnés comme pré-diffusés")

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
        if not obj.is_published:
            url = "{url}?ticket={ticket}".format(
                url=url,
                querystring=obj.prepublication_ticket
            )
        return format_html(
            '<a href={}>{}</a>', url, _("Voir sur le site")
        )
    view_issue_on_site.short_description = _("Voir le numéro sur le site")


class ArticleExternalStatusFilter(admin.SimpleListFilter):
    title = "Lien Externe"
    parameter_name = 'external_status'
    query_field_name = 'external_url'

    def lookups(self, request, model_admin):
        return (
            ('yes', "Oui"),
            ('no', "Non"),
        )

    def queryset(self, request, queryset):
        fn = self.query_field_name
        external_is_empty = Q(**{'%s__isnull' % fn: True}) | Q(**{fn: ''})
        if self.value() == 'yes':
            return queryset.filter(~external_is_empty)
        if self.value() == 'no':
            return queryset.filter(external_is_empty)


class ArticleExternalPDFStatusFilter(ArticleExternalStatusFilter):
    title = "Lien PDF Externe"
    parameter_name = 'external_pdf_status'
    query_field_name = 'external_pdf_url'


class ArticleAdmin(admin.ModelAdmin):

    readonly_fields = (
        'issue', 'type', 'article_title', 'doi', 'localidentifier', 'article_journal',
        'fedora_created', 'fedora_updated',
    )

    list_display = (
        'localidentifier',
        'issue__localidentifier',
        'issue__year',
        'title',
        'external_status',
    )
    raw_id_fields = ('issue', )
    search_fields = ('id', 'localidentifier', )
    list_filter = (
        'type',
        ArticleExternalStatusFilter,
        ArticleExternalPDFStatusFilter,
        'issue__journal__collection',
        'issue__journal',
        'issue__year')

    def issue__localidentifier(self, obj):
        return obj.issue.localidentifier

    issue__localidentifier.short_description = "Numéro"
    issue__localidentifier.admin_order_field = 'issue__localidentifier'

    def issue__year(self, obj):
        return obj.issue.year

    issue__year.short_description = "Année"
    issue__year.admin_order_field = 'issue__year'

    def article_title(self, obj):
        return obj.title

    def article_journal(self, obj):
        return obj.issue.journal

    article_journal.short_description = 'Revue'
    article_title.short_description = "Titre de l'article"

    def external_status(self, obj):
        if obj.external_url:
            if obj.external_pdf_url:
                return "HTML + PDF"
            else:
                return "HTML"
        else:
            if obj.external_pdf_url:
                return "PDF"
            else:
                return "Non"

    external_status.short_description = 'Externe?'

    fieldsets = [
        ('Identification', {
            'fields': (
                ('localidentifier', 'type'),
                ('article_title',),
                ('article_journal', 'issue',),
            ),
        }),
        ("Synchronisation", {
            'fields': (
                ('fedora_created', 'fedora_updated', )
            )
        }),
        ("Localisation de l'article", {
            'fields': (
                'external_url', 'external_pdf_url',
            )
        }),

        ("Restrictions d'accès", {
            'fields': (
                'publication_allowed',
            )
        }),
    ]


class JournalInformationAdmin(TranslationAdmin):
    pass


class JournalTypeAdmin(TranslationAdmin):
    pass


admin.site.register(Journal, JournalAdmin)
admin.site.register(Issue, IssueAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(JournalInformation, JournalInformationAdmin)
admin.site.unregister(JournalType)
admin.site.register(JournalType, JournalTypeAdmin)
