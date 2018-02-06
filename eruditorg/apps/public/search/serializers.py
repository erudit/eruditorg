# -*- coding: utf-8 -*-

from apps.public.search.models import ResearchReport, Book, GenericSolrDocument
from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.utils import translation
from django.utils.translation import ugettext as _
from eulfedora.util import RequestFailed
from requests.exceptions import ConnectionError
from rest_framework import serializers

from erudit import models as erudit_models
from erudit.templatetags.model_formatters import person_list


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
            ResearchReport: 'report',
            Book: 'book',
            GenericSolrDocument: 'generic',
        }[obj.__class__]

    def get_real_object(self, obj):
        if isinstance(obj, ResearchReport):
            return GenericSolrDocumentSerializer(obj).data
        if isinstance(obj, Book):
            return GenericSolrDocumentSerializer(obj).data
        if isinstance(obj, GenericSolrDocument):
            return GenericSolrDocumentSerializer(obj).data

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
    collection = serializers.SerializerMethodField()
    reviewed_works = serializers.SerializerMethodField()
    paral_titles = serializers.SerializerMethodField()
    paral_subtitles = serializers.SerializerMethodField()
    journal_code = serializers.SerializerMethodField()
    series = serializers.SerializerMethodField()
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
    pdf_url = serializers.SerializerMethodField()

    class Meta:
        model = erudit_models.Article
        fields = [
            'journal_code', 'series', 'journal_type', 'journal_url', 'issue_localidentifier',
            'issue_title', 'issue_url', 'issue_number', 'paral_titles', 'paral_subtitles',
            'issue_volume', 'issue_published', 'issue_volume_slug', 'publication_date',
            'title', 'surtitle', 'subtitle',
            'processing', 'authors', 'abstract', 'type', 'first_page', 'last_page', 'pdf_url',
            'external_url', 'external_pdf_url', 'collection', 'reviewed_works',
        ]

    def get_authors(self, obj):
        return obj.get_formatted_authors()

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

    def get_collection(self, obj):
        return obj.issue.journal.collection.name

    def get_reviewed_works(self, obj):
        if obj.fedora_object and obj.fedora_object.exists:
            return obj.erudit_object.get_reviewed_works()

    def get_journal_code(self, obj):
        return obj.issue.journal.code

    def get_series(self, obj):
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

    def get_pdf_url(self, obj):
        if obj.external_pdf_url:
            # If we have a external_pdf_url, then it's always the proper one to return.
            return obj.external_pdf_url
        if obj.issue.external_url:
            # special case. if our issue has an external_url, regardless of whether we have a
            # fedora object, we *don't* have a PDF url. See the RECMA situation at #1651
            return None
        try:
            if obj.fedora_object:
                return reverse('public:journal:article_raw_pdf', kwargs={
                    'journal_code': obj.issue.journal.code,
                    'issue_slug': obj.issue.volume_slug,
                    'issue_localid': obj.issue.localidentifier,
                    'localid': obj.localidentifier,
                })
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
        return str(obj.author)

    def get_collection_name(self, obj):
        return obj.collection.name

    def get_publication_date(self, obj):
        return obj.publication_year

    def get_description(self, obj):
        return obj.description

    def get_keywords(self, obj):
        return [keyword.name for keyword in obj.keywords.all()]


class GenericSolrDocumentSerializer(serializers.Serializer):

    numero = serializers.SerializerMethodField()
    authors = serializers.SerializerMethodField()
    pages = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    volume = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    collection = serializers.SerializerMethodField()
    issn = serializers.SerializerMethodField()
    publication_date = serializers.SerializerMethodField()
    year = serializers.SerializerMethodField()
    series = serializers.SerializerMethodField()

    def get_year(self, obj):
        if 'Annee' in obj.data:
            return obj.data.get('Annee')[0]

    def get_publication_date(self, obj):
        return obj.data.get('AnneePublication')

    def get_issn(self, obj):
        return obj.data.get('ISSN')

    def get_collection(self, obj):
        return obj.data.get('Fonds_fac')

    def get_authors(self, obj):

        return person_list(obj.data.get('AuteurNP_fac'))

    def get_volume(self, obj):
        return obj.data.get('Volume')

    def get_series(self, obj):
        collection_title = obj.data.get('TitreCollection_fac')
        if collection_title:
            return collection_title[0]
        return None

    def get_url(self, obj):
        return obj.data['URLDocument'][0]

    def get_numero(self, obj):
        return obj.data.get('Numero')

    def get_pages(self, obj):
        if not {'PremierePage', 'DernierePage'}.issubset(set(obj.data.keys())):
            return None
        return _('Pages {firstpage}-{lastpage}'.format(
            firstpage=obj.data['PremierePage'],
            lastpage=obj.data['DernierePage']
        ))

    def get_title(self, obj):
        TITLE_ATTRS = ['Titre_fr', 'Titre_en', 'TitreRefBiblio_aff']
        for attrname in TITLE_ATTRS:
            if attrname in obj.data:
                return obj.data[attrname]
        return _("(Sans titre)")

    class Meta:
        model = GenericSolrDocument
        fields = [
            'Numero', 'PremierePage', 'TypePublication_fac', 'MIMEType', 'RevueID',
            'Volume', 'NumeroID', 'TitreCollection_fac', 'Langue', 'DernierePage',
            'URLDocument', 'Corpus_fac', 'TypeArticle_fac', 'Fonds_fac', 'RevueAbr',
            'ISSN', 'AnneePublication', 'ID', 'AuteurNP_fac', 'Annee', 'Auteur_tri',
            'Auteur_fac', 'TitreRefBiblio_aff', 'DateAjoutErudit', 'DateAjoutIndex'
        ]
