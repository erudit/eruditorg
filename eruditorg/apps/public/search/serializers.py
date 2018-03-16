from django.utils.translation import ugettext as _
from rest_framework import serializers

from erudit.templatetags.model_formatters import person_list


class GenericSolrDocumentSerializer(serializers.Serializer):
    localidentifier = serializers.SerializerMethodField()
    document_type = serializers.SerializerMethodField()
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

    def get_localidentifier(self, obj):
        return obj['ID']

    def get_document_type(self, obj):
        corpus = obj['Corpus_fac']
        return {
            'Article': 'article',
            'Culturel': 'article',
            'Thèses': 'thesis',
            'Dépot': 'report',
            'Livres': 'book',
            'Actes': 'book',
            'Rapport': 'report',
        }.get(corpus, 'generic')

    def get_year(self, obj):
        if 'Annee' in obj:
            return obj.get('Annee')[0]

    def get_publication_date(self, obj):
        return obj.get('AnneePublication')

    def get_issn(self, obj):
        return obj.get('ISSN')

    def get_collection(self, obj):
        return obj.get('Fonds_fac')

    def get_authors(self, obj):

        return person_list(obj.get('AuteurNP_fac'))

    def get_volume(self, obj):
        return obj.get('Volume')

    def get_series(self, obj):
        collection_title = obj.get('TitreCollection_fac')
        if collection_title:
            return collection_title[0]
        return None

    def get_url(self, obj):
        if 'URLDocument' in obj:
            return obj['URLDocument'][0]
        else:
            return None

    def get_numero(self, obj):
        return obj.get('Numero')

    def get_pages(self, obj):
        if not {'PremierePage', 'DernierePage'}.issubset(set(obj.keys())):
            return None
        return _('Pages {firstpage}-{lastpage}'.format(
            firstpage=obj['PremierePage'],
            lastpage=obj['DernierePage']
        ))

    def get_title(self, obj):
        TITLE_ATTRS = ['Titre_fr', 'Titre_en', 'TitreRefBiblio_aff']
        for attrname in TITLE_ATTRS:
            if attrname in obj:
                return obj[attrname]
        return _("(Sans titre)")
