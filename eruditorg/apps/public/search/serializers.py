# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.utils import translation
from django.utils.translation import ugettext as _
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
            if real_object_data is not None:
                cache.set(cache_key, real_object_data, 60 * 60)

        return real_object_data


class ArticleSerializer(serializers.ModelSerializer):
    authors = serializers.SerializerMethodField()
    abstract = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    collection_name = serializers.SerializerMethodField()
    reviewed_works = serializers.SerializerMethodField()
    paral_titles = serializers.SerializerMethodField()
    paral_subtitles = serializers.SerializerMethodField()
    journal_code = serializers.SerializerMethodField()
    journal_name = serializers.SerializerMethodField()
    journal_type = serializers.SerializerMethodField()
    journal_url = serializers.SerializerMethodField()
    issue_url = serializers.SerializerMethodField()
    issue_localidentifier = serializers.SerializerMethodField()
    issue_title = serializers.SerializerMethodField()
    issue_number = serializers.SerializerMethodField()
    issue_volume = serializers.SerializerMethodField()
    issue_published = serializers.SerializerMethodField()
    issue_volume_slug = serializers.SerializerMethodField()
    publication_date = serializers.SerializerMethodField()
    has_pdf = serializers.SerializerMethodField()

    class Meta:
        model = erudit_models.Article
        fields = [
            'journal_code', 'journal_name', 'journal_type', 'journal_url', 'issue_localidentifier',
            'issue_title', 'issue_url', 'issue_number', 'paral_titles', 'paral_subtitles',
            'issue_volume', 'issue_published', 'issue_volume_slug', 'publication_date',
            'title', 'surtitle', 'subtitle',
            'processing', 'authors', 'abstract', 'type', 'first_page', 'last_page', 'has_pdf',
            'external_url', 'external_pdf_url', 'collection_name', 'reviewed_works',
        ]

    def get_authors(self, obj):
        if obj.get_fedora_object():
            article_object = obj.erudit_object
            return article_object.get_authors()
        authors = []
        for author in obj.authors.all():
            authors.append({
                'firstname': author.firstname,
                'lastname': author.lastname,
                'othername': author.othername,
            })
        return authors

    def get_type(self, obj):
        if obj.type:
            return obj.get_type_display()
        return _('Article')

    def get_paral_titles(self, obj):
        paral_titles = obj.titles.filter(paral=True)
        return list(t.title for t in paral_titles)

    def get_paral_subtitles(self, obj):
        paral_subtitles = obj.subtitles.filter(paral=True)
        return list(t.title for t in paral_subtitles)

    def get_abstract(self, obj):
        return obj.abstract

    def get_collection_name(self, obj):
        return obj.issue.journal.collection.name

    def get_reviewed_works(self, obj):
        if obj.get_fedora_object():
            return obj.erudit_object.get_reviewed_works()

    def get_journal_code(self, obj):
        return obj.issue.journal.code

    def get_journal_name(self, obj):
        return obj.issue.journal.name

    def get_journal_type(self, obj):
        if obj.issue.journal.type:
            return obj.issue.journal.type.get_code_display().lower()
        return ''

    def get_publication_date(self, obj):
        return obj.issue.abbreviated_volume_title

    def get_journal_url(self, obj):
        journal = obj.issue.journal
        if journal.external_url:
            return journal.external_url
        return reverse('public:journal:journal_detail', args=(journal.code, ))

    def get_issue_url(self, obj):
        issue = obj.issue
        if issue.external_url:
            return issue.external_url
        return reverse('public:journal:issue_detail', args=(
            issue.journal.code,
            issue.volume_slug,
            issue.localidentifier,
        ))

    def get_issue_localidentifier(self, obj):
        return obj.issue.localidentifier

    def get_issue_title(self, obj):
        return obj.issue.name_with_themes

    def get_issue_number(self, obj):
        return obj.issue.number_for_display

    def get_issue_volume(self, obj):
        return obj.issue.volume

    def get_issue_published(self, obj):
        return obj.issue.publication_period or obj.issue.year

    def get_issue_volume_slug(self, obj):
        return obj.issue.volume_slug

    def get_has_pdf(self, obj):
        try:
            return obj.external_pdf_url is not None or (
                obj.fedora_object and obj.fedora_object.pdf.exists)
        except (RequestFailed, ConnectionError):  # pragma: no cover
            if settings.DEBUG:
                return False
            raise


class ThesisSerializer(serializers.ModelSerializer):
    authors = serializers.SerializerMethodField()
    collection_name = serializers.SerializerMethodField()
    publication_date = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    keywords = serializers.SerializerMethodField()

    class Meta:
        model = erudit_models.Thesis
        fields = [
            'title', 'url', 'publication_date', 'description', 'authors', 'collection',
            'collection_name', 'description', 'keywords'
        ]

    def get_authors(self, obj):
        return [{
            'lastname': obj.author.lastname,
            'firstname': obj.author.firstname,
            'othername': obj.author.othername,
        }]

    def get_collection_name(self, obj):
        return obj.collection.name

    def get_publication_date(self, obj):
        return obj.publication_year

    def get_description(self, obj):
        return obj.description

    def get_keywords(self, obj):
        return [keyword.name for keyword in obj.keywords.all()]
