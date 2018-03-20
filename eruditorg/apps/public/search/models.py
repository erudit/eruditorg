from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from eulfedora.util import RequestFailed
from requests.exceptions import ConnectionError

from erudit import models as erudit_models
from erudit.templatetags.model_formatters import person_list


class Generic:
    def __init__(self, solr_data):
        self.localidentifier = solr_data['ID']
        self.corpus = solr_data['Corpus_fac']
        self.solr_data = solr_data

    def can_cite(self):
        return False

    @property
    def document_type(self):
        return {
            'Dépot': 'report',
            'Livres': 'book',
            'Actes': 'book',
            'Rapport': 'report',
        }.get(self.corpus, 'generic')

    @property
    def year(self):
        return self.solr_data['Annee'][0] if 'Annee' in self.solr_data else None

    @property
    def publication_date(self):
        return self.solr_data.get('AnneePublication')

    @property
    def issn(self):
        return self.solr_data.get('ISSN')

    @property
    def collection(self):
        return self.solr_data.get('Fonds_fac')

    @property
    def authors(self):
        return person_list(self.solr_data.get('AuteurNP_fac'))

    @property
    def volume(self):
        return self.solr_data.get('Volume')

    @property
    def series(self):
        collection_title = self.solr_data.get('TitreCollection_fac')
        if collection_title:
            return collection_title[0]
        else:
            return None

    @property
    def url(self):
        return self.solr_data['URLDocument'][0] if 'URLDocument' in self.solr_data else None

    @property
    def numero(self):
        return self.solr_data.get('Numero')

    @property
    def pages(self):
        if not {'PremierePage', 'DernierePage'}.issubset(set(self.solr_data.keys())):
            return None
        else:
            return _('Pages {firstpage}-{lastpage}'.format(
                firstpage=self.solr_data['PremierePage'],
                lastpage=self.solr_data['DernierePage']
            ))

    @property
    def title(self):
        TITLE_ATTRS = ['Titre_fr', 'Titre_en', 'TitreRefBiblio_aff']
        for attrname in TITLE_ATTRS:
            if attrname in self.solr_data:
                return self.solr_data[attrname]
        return _("(Sans titre)")


# These models below are temporary shims that we implement with the same API as the old serializers
# but we instantiate them on the "other side" of the REST API. We do this to ease the transition.
# otherwise, we would have to change the search result template at the same time as we strip the
# django rest framework.


class Article(Generic):
    def __init__(self, solr_data):
        super().__init__(solr_data)
        self.obj = erudit_models.Article.objects.get(localidentifier=self.localidentifier)
        self.id = self.obj.id

    def __getattr__(self, name):
        return getattr(self.obj, name)

    def can_cite(self):
        # We cannot cite articles we don't have in fedora. ref #1491
        return self.obj.is_in_fedora

    @property
    def document_type(self):
        return 'article'

    @property
    def authors(self):
        if self.obj.is_in_fedora:
            return self.obj.get_formatted_authors()
        else:
            return super().authors

    @property
    def authors_mla(self):
        # TODO: call with style arg after liberuditarticle update
        return self.authors

    @property
    def authors_apa(self):
        # TODO: call with style arg after liberuditarticle update
        return self.authors

    @property
    def authors_chicago(self):
        # TODO: call with style arg after liberuditarticle update
        return self.authors

    @property
    def type(self):
        if self.obj.type:
            return self.obj.get_type_display()
        return _('Article')

    @property
    def title(self):
        if self.obj.is_in_fedora:
            return self.obj.title
        else:
            return super().title

    @property
    def paral_titles(self):
        paral_titles = self.obj.titles.filter(paral=True)
        return list(t.title for t in paral_titles)

    @property
    def paral_subtitles(self):
        paral_subtitles = self.obj.subtitles.filter(paral=True)
        return list(t.title for t in paral_subtitles)

    @property
    def abstract(self):
        return self.obj.abstract

    @property
    def collection(self):
        return self.obj.issue.journal.collection.name

    @property
    def reviewed_works(self):
        if self.obj.fedora_object and self.obj.fedora_object.exists:
            return self.obj.erudit_object.get_reviewed_works()

    @property
    def journal_code(self):
        return self.obj.issue.journal.code

    @property
    def series(self):
        return self.obj.issue.journal.name

    @property
    def journal_type(self):
        if self.obj.issue.journal.type:
            return self.obj.issue.journal.type.get_code_display().lower()
        return ''

    @property
    def publication_date(self):
        return self.obj.issue.abbreviated_volume_title

    @property
    def journal_url(self):
        journal = self.obj.issue.journal
        if journal.external_url:
            return journal.external_url
        return reverse('public:journal:journal_detail', args=(journal.code, ))

    @property
    def issue_url(self):
        issue = self.obj.issue
        if issue.external_url:
            return issue.external_url
        return reverse('public:journal:issue_detail', args=(
            issue.journal.code,
            issue.volume_slug,
            issue.localidentifier,
        ))

    @property
    def issue_localidentifier(self):
        return self.obj.issue.localidentifier

    @property
    def issue_title(self):
        return self.obj.issue.name_with_themes

    @property
    def issue_number(self):
        return self.obj.issue.number_for_display

    @property
    def issue_volume(self):
        return self.obj.issue.volume

    @property
    def issue_published(self):
        return self.obj.issue.publication_period or self.obj.issue.year

    @property
    def issue_volume_slug(self):
        return self.obj.issue.volume_slug

    @property
    def pdf_url(self):
        if self.obj.external_pdf_url:
            # If we have a external_pdf_url, then it's always the proper one to return.
            return self.obj.external_pdf_url
        if self.obj.issue.external_url:
            # special case. if our issue has an external_url, regardless of whether we have a
            # fedora object, we *don't* have a PDF url. See the RECMA situation at #1651
            return None
        try:
            if self.obj.fedora_object:
                return reverse('public:journal:article_raw_pdf', kwargs={
                    'journal_code': self.obj.issue.journal.code,
                    'issue_slug': self.obj.issue.volume_slug,
                    'issue_localid': self.obj.issue.localidentifier,
                    'localid': self.obj.localidentifier,
                })
        except (RequestFailed, ConnectionError):  # pragma: no cover
            if settings.DEBUG:
                return False
            raise

    @property
    def keywords(self):
        return [keyword.name for keyword in self.obj.keywords.all()]


class Thesis(Generic):
    def __init__(self, solr_data):
        super().__init__(solr_data)
        self.obj = erudit_models.Thesis.objects.get(localidentifier=self.localidentifier)
        self.id = self.obj.id

    def __getattr__(self, name):
        return getattr(self.obj, name)

    def can_cite(self):
        return True

    @property
    def document_type(self):
        return 'thesis'

    @property
    def authors(self):
        return str(self.obj.author)

    @property
    def collection(self):
        return self.obj.collection.code

    @property
    def collection_name(self):
        return self.obj.collection.name

    @property
    def publication_date(self):
        return self.obj.publication_year

    @property
    def description(self):
        return self.obj.description

    @property
    def keywords(self):
        return [keyword.name for keyword in self.obj.keywords.all()]


def get_model_instance(solr_data):
    corpus = solr_data['Corpus_fac']
    doctype = {
        'Article': 'article',
        'Culturel': 'article',
        'Thèses': 'thesis',
    }.get(corpus, 'generic')
    if doctype == 'thesis':
        try:
            return Thesis(solr_data)
        except ObjectDoesNotExist:
            pass
    elif doctype == 'article':
        try:
            return Article(solr_data)
        except ObjectDoesNotExist:
            pass

    return Generic(solr_data)
