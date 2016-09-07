# -*- coding: utf-8 -*-

from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from ..models import Article
from ..models import ArticleAbstract
from ..models import ArticleSectionTitle
from ..models import Issue
from ..models import IssueTheme
from ..models import Journal
from ..models import JournalInformation


class JournalDisciplineInline(admin.TabularInline):
    model = Journal.disciplines.through


class JournalAdmin(admin.ModelAdmin):
    search_fields = ('code', 'name', 'issn_print', 'issn_web', 'external_url', )
    list_display = ('__str__', 'code', 'type', 'open_access', 'external_url', 'active', )
    list_display_links = ('__str__', 'code', )
    list_filter = ('collection', 'publishers', 'type', 'paper', 'open_access', 'active', )
    filter_horizontal = ('members', 'publishers', )

    fieldsets = [
        ('Identification', {
            'fields': (
                ('collection', ),
                ('code', 'previous_journal', 'next_journal', ),
                ('localidentifier', ),
                ('name', ),
                ('subtitle', ),
                ('issn_print', 'issn_web', ),
                ('website_url', ),
            ),
        }),
        (None, {
            'fields': (
                ('publishers',),
                ('type'),
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


class IssueAdmin(admin.ModelAdmin):
    inlines = (IssueThemeInline, )
    list_display = ('journal', 'year', 'volume', 'number', 'title', 'localidentifier', )
    search_fields = ('id', 'localidentifier', )
    list_filter = ('journal__collection', )


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


class ArticleAdmin(admin.ModelAdmin):
    inlines = (ArticleAbstractInline, ArticleSectionTitleInline, )
    list_display = ('localidentifier', 'title', )
    raw_id_fields = ('issue', 'publisher', 'authors', )
    search_fields = ('id', 'title', 'localidentifier', )


class JournalInformationAdmin(TranslationAdmin):
    pass


admin.site.register(Journal, JournalAdmin)
admin.site.register(Issue, IssueAdmin)
admin.site.register(IssueTheme, IssueThemeAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(ArticleAbstract, ArticleAbstractAdmin)
admin.site.register(ArticleSectionTitle, ArticleSectionTitleAdmin)
admin.site.register(JournalInformation, JournalInformationAdmin)
