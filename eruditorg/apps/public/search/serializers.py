# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.cache import cache
from django.utils import translation
from eulfedora.util import RequestFailed
from requests.exceptions import ConnectionError
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
        cache_key = 'eruditdocument-real-object-serialized-{}-{}'.format(
            obj.id, translation.get_language())
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
    collection_name = serializers.SerializerMethodField()
    journal_code = serializers.SerializerMethodField()
    issue_localidentifier = serializers.SerializerMethodField()
    issue_title = serializers.SerializerMethodField()
    issue_number = serializers.SerializerMethodField()
    issue_published = serializers.SerializerMethodField()
    issue_volume_slug = serializers.SerializerMethodField()
    has_pdf = serializers.SerializerMethodField()

    class Meta:
        model = erudit_models.Article
        fields = [
            'journal_code', 'issue_localidentifier', 'issue_title', 'issue_number',
            'issue_published', 'issue_volume_slug', 'title', 'surtitle', 'subtitle', 'processing',
            'authors', 'abstract', 'first_page', 'last_page', 'has_pdf', 'external_url',
            'collection_name',
        ]

    def get_authors(self, obj):
        authors = []
        for author in obj.authors.all():
            authors.append({
                'firstname': author.firstname,
                'lastname': author.lastname,
                'othername': author.othername,
            })
        return authors

    def get_abstract(self, obj):
        return obj.abstract

    def get_collection_name(self, obj):
        return obj.issue.journal.collection.name

    def get_journal_code(self, obj):
        return obj.issue.journal.code

    def get_issue_localidentifier(self, obj):
        return obj.issue.localidentifier

    def get_issue_title(self, obj):
        return obj.issue.title

    def get_issue_number(self, obj):
        return obj.issue.number_for_display

    def get_issue_published(self, obj):
        return obj.issue.publication_period or obj.issue.year

    def get_issue_volume_slug(self, obj):
        return obj.issue.volume_slug

    def get_has_pdf(self, obj):
        try:
            return obj.fedora_object.pdf.exists
        except (RequestFailed, ConnectionError):  # pragma: no cover
            if settings.DEBUG:
                return False
            raise


class ThesisSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    collection_name = serializers.SerializerMethodField()

    class Meta:
        model = erudit_models.Thesis
        fields = [
            'title', 'url', 'publication_year', 'description', 'author', 'collection',
            'collection_name',
        ]

    def get_author(self, obj):
        return {
            'lastname': obj.author.lastname,
            'firstname': obj.author.firstname,
            'othername': obj.author.othername,
        }

    def get_collection_name(self, obj):
        return obj.collection.name
