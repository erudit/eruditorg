# -*- coding: utf-8 -*-

from django.core.cache import cache
from django.utils import formats
from django.utils import translation
from rest_framework import serializers

from .. import models as erudit_models


class EruditDocumentSerializer(serializers.ModelSerializer):
    real_object = serializers.SerializerMethodField()

    class Meta:
        model = erudit_models.EruditDocument
        fields = ['id', 'localidentifier', 'real_object', ]

    def get_real_object(self, obj):
        cache_key = 'eruditdocument-real-object-serialized-{}'.format(obj.id)
        real_object_data = cache.get(cache_key, None)

        if real_object_data is None:
            # This method should return a serialized representation of an Érudit document ; it could
            # be an article, a thesis, a book, ...
            # However there is a problem: it not currently possible to determine the correct model
            # associated with an EruditDocument instance. For now we use only Article objects so we
            # will make the assumption that all Érudit documents are article... But this problem
            # should be resolved using polymorphism.
            article = erudit_models.Article.objects.select_related('issue', 'issue__journal') \
                .get(id=obj.id)
            real_object_data = ArticleSerializer(article).data
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
