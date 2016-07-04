# -*- coding: utf-8 -*-

from django.core.cache import cache
from django.utils import formats
from django.utils import translation
from rest_framework import serializers

from erudit import models as erudit_models


class EruditDocumentSerializer(serializers.ModelSerializer):
    document_type = serializers.SerializerMethodField()
    real_object = serializers.SerializerMethodField()

    class Meta:
        model = erudit_models.EruditDocument
        fields = ['id', 'localidentifier', 'document_type', 'real_object', ]

    def get_document_type(self, obj):
        return {
            erudit_models.Article: 'article',
            erudit_models.Thesis: 'thesis',
        }[obj.__class__]

    def get_real_object(self, obj):
        cache_key = 'eruditdocument-real-object-serialized-{}'.format(obj.id)
        real_object_data = cache.get(cache_key, None)

        if real_object_data is None:
            if isinstance(obj, erudit_models.Article):
                real_object_data = ArticleSerializer(obj).data
            elif isinstance(obj, erudit_models.Thesis):
                real_object_data = ThesisSerializer(obj).data
            # Caches the content of the object for 1 hour
            cache.set(cache_key, real_object_data, 60 * 60)

        return real_object_data


class ArticleSerializer(serializers.ModelSerializer):
    authors = serializers.SerializerMethodField()
    abstract = serializers.SerializerMethodField()
    first_page = serializers.SerializerMethodField()
    last_page = serializers.SerializerMethodField()
    subtitle = serializers.SerializerMethodField()
    journal_code = serializers.SerializerMethodField()
    issue_localidentifier = serializers.SerializerMethodField()
    issue_title = serializers.SerializerMethodField()
    issue_number = serializers.SerializerMethodField()
    issue_published = serializers.SerializerMethodField()

    class Meta:
        model = erudit_models.Article
        fields = [
            'journal_code', 'issue_localidentifier', 'issue_title', 'issue_number',
            'issue_published', 'title', 'surtitle', 'subtitle', 'processing', 'authors', 'abstract',
            'first_page', 'last_page',
        ]

    def get_authors(self, obj):
        return obj.erudit_object.authors

    def get_abstract(self, obj):
        abstracts = obj.erudit_object.abstracts
        lang = translation.get_language()
        _abstract = list(filter(lambda r: r['lang'] == lang, abstracts))

        abstract = None
        if len(_abstract):
            abstract = _abstract[0]['content']
        elif len(abstracts):
            abstract = abstracts[0]['content']

        return abstract

    def get_first_page(self, obj):
        return obj.erudit_object.first_page

    def get_last_page(self, obj):
        return obj.erudit_object.last_page

    def get_subtitle(self, obj):
        return obj.erudit_object.subtitle

    def get_journal_code(self, obj):
        return obj.issue.journal.code

    def get_issue_localidentifier(self, obj):
        return obj.issue.localidentifier

    def get_issue_title(self, obj):
        return obj.issue.title

    def get_issue_number(self, obj):
        return obj.issue.erudit_object.number

    def get_issue_published(self, obj):
        return formats.date_format(obj.issue.date_published, 'YEAR_MONTH_FORMAT')


class ThesisSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta:
        model = erudit_models.Thesis
        fields = [
            'title', 'url', 'publication_year', 'description', 'author', 'collection',
        ]

    def get_author(self, obj):
        return {
            'lastname': obj.author.lastname,
            'firstname': obj.author.firstname,
        }
