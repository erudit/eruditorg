# -*- coding: utf-8 -*-

from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from ..models import Article
from ..models import Issue
from ..models import Journal
from ..models import JournalInformation


class JournalDisciplineInline(admin.TabularInline):
    model = Journal.disciplines.through


class JournalAdmin(admin.ModelAdmin):
    search_fields = ('code', 'name', 'issn_print', 'issn_web', 'url', )
    list_display = ('__str__', 'code', 'type', 'open_access', 'url', 'active', )
    list_display_links = ('__str__', 'code', )
    list_filter = ('publishers', 'type', 'paper', 'open_access', 'active', )
    filter_horizontal = ('members', 'publishers', )
    list_editable = ('type', 'active', )

    fieldsets = [
        ('Identification', {
            'fields': (
                ('collection', ),
                ('code', 'formerly'),
                ('localidentifier',),
                ('name', ),
                ('subtitle',),
                ('issn_print', 'issn_web'),
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
        ('Coordonnées', {
            'classes': ('collapse',),
            'fields': (
                'url',
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
    search_fields = ('id', 'localidentifier', )
    list_display = ('journal', 'year', 'volume', 'number', 'title', 'localidentifier', )


class ArticleAdmin(admin.ModelAdmin):
    search_fields = ('id', 'title', 'localidentifier', )
    list_display = ('issue', 'localidentifier', 'title', )
    list_filter = ('issue', )


class DisciplineInline(admin.TabularInline):
    model = Journal.disciplines.through


class JournalInformationAdmin(TranslationAdmin):
    pass


admin.site.register(Journal, JournalAdmin)
admin.site.register(Issue, IssueAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(JournalInformation, JournalInformationAdmin)
