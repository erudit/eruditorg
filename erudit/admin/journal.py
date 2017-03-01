# -*- coding: utf-8 -*-

from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext as _

from ..models import Article
from ..models import ArticleAbstract
from ..models import ArticleSectionTitle
from ..models import Issue
from ..models import IssueTheme
from ..models import IssueContributor
from ..models import Journal
from ..models import JournalInformation
from ..models import ArticleTitle
from ..models import ArticleSubtitle


class JournalDisciplineInline(admin.TabularInline):
    model = Journal.disciplines.through


class JournalAdmin(admin.ModelAdmin):
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


class IssueThemeAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'name', 'subname', )
    list_display_links = ('identifier', 'name', )
    raw_id_fields = ('issue', )


class IssueThemeInline(admin.TabularInline):
    extra = 0
    model = IssueTheme


class IssueContributorInline(admin.TabularInline):
    extra = 0
    model = IssueContributor


class IssueAdmin(admin.ModelAdmin):
    inlines = (IssueThemeInline, IssueContributorInline)
    list_display = (
        'journal', 'year', 'volume', 'number', 'title', 'localidentifier',
        'view_issue_on_site', )
    search_fields = ('id', 'localidentifier', )
    list_filter = ('is_published', 'journal__collection', 'journal__name', )
    actions = [
        'make_published', 'make_unpublished',
        'force_free_access_to_true', 'force_free_access_to_false',
    ]

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
        return format_html(
            '<a href={}>{}</a>', url, _("Voir sur le site")
        )
    view_issue_on_site.short_description = _("Voir le numéro sur le site")


class ArticleAbstractAdmin(admin.ModelAdmin):
    list_display = ('id', '__str__', 'language', )
    list_display_links = ('id', '__str__', )
    raw_id_fields = ('article', )


class ArticleAbstractInline(admin.TabularInline):
    extra = 0
    model = ArticleAbstract


class ArticleSectionTitleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'level', )
    list_display_links = ('id', 'title', )
    raw_id_fields = ('article', )


class ArticleSectionTitleInline(admin.TabularInline):
    extra = 0
    model = ArticleSectionTitle


class ArticleTitleInline(admin.TabularInline):
    extra = 0
    model = ArticleTitle


class ArticleSubtitleInline(admin.TabularInline):
    extra = 0
    model = ArticleSubtitle


class ArticleAuthorInline(admin.TabularInline):
    extra = 0
    model = Article.authors.through


class ArticleAdmin(admin.ModelAdmin):

    def issue__localidentifier(self, obj):
        return obj.issue.localidentifier

    inlines = (
        ArticleAbstractInline, ArticleSectionTitleInline, ArticleTitleInline,
        ArticleSubtitleInline, ArticleAuthorInline
    )
    list_display = ('localidentifier', 'issue__localidentifier', 'title', )
    raw_id_fields = ('issue', 'publisher', 'authors', )
    search_fields = ('id', 'localidentifier', 'titles__title', )

    list_filter = ('type', 'issue__journal__collection', )


class JournalInformationAdmin(TranslationAdmin):
    pass


admin.site.register(Journal, JournalAdmin)
admin.site.register(Issue, IssueAdmin)
admin.site.register(IssueTheme, IssueThemeAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(ArticleAbstract, ArticleAbstractAdmin)
admin.site.register(ArticleSectionTitle, ArticleSectionTitleAdmin)
admin.site.register(JournalInformation, JournalInformationAdmin)
