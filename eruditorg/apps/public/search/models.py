from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _, get_language
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


# These models below are wrappers around their corresponding models in `erudit.models`. For thesis,
# it's mostly noise that's present for legacy reasons, but for articles, this wrapper allows us to
# properly fall back to solr data when we're in the presence of an out-of-fedora article while still
# output the search result as an article transparently in the template.


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

    def cite_url(self, type):
        return reverse('public:journal:article_citation_{}'.format(type), kwargs={
            'journal_code': self.obj.issue.journal.code,
            'issue_slug': self.obj.issue.volume_slug,
            'issue_localid': self.obj.issue.localidentifier,
            'localid': self.localidentifier,
        })

    def cite_enw_url(self):
        return self.cite_url('enw')

    def cite_bib_url(self):
        return self.cite_url('bib')

    def cite_ris_url(self):
        return self.cite_url('ris')

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
        return self.obj.get_formatted_authors(style='mla')

    @property
    def authors_apa(self):
        return self.obj.get_formatted_authors(style='apa')

    @property
    def authors_chicago(self):
        return self.obj.get_formatted_authors(style='chicago')

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
        if self.obj.is_in_fedora:
            titles = self.obj.erudit_object.get_titles()
            # NOTE: 'equivalent' is supposed to be for parallel titles that aren't in an officially
            # supported language, but the old "django import" method also imported equivalent
            # titles, so to stay in line with the old behavior, we keep 'equivalent' in. But we
            # might want to change that.
            return titles['paral'] + titles['equivalent']
        else:
            return []

    @property
    def abstract(self):
        if self.obj.is_in_fedora:
            return self.obj.abstract
        else:
            return ''

    @property
    def collection(self):
        return self.obj.issue.journal.collection.name

    @property
    def reviewed_works(self):
        if self.obj.fedora_object and self.obj.fedora_object.exists:
            return self.obj.erudit_object.get_reviewed_works()

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
        if self.is_in_fedora:
            lang = get_language()
            keyword_sets = self.obj.erudit_object.get_keywords()
            for keyword_set in keyword_sets:
                if keyword_set['lang'] == lang:
                    return keyword_set['keywords']
        return []


class Thesis(Generic):
    def __init__(self, solr_data):
        super().__init__(solr_data)
        self.obj = erudit_models.Thesis.objects.get(localidentifier=self.localidentifier)
        self.id = self.obj.id

    def __getattr__(self, name):
        return getattr(self.obj, name)

    def can_cite(self):
        return True

    def cite_url(self, type):
        return reverse('public:thesis:thesis_citation_{}'.format(type), args=[
            self.collection,
            self.id,
        ])

    def cite_enw_url(self):
        return self.cite_url('enw')

    def cite_bib_url(self):
        return self.cite_url('bib')

    def cite_ris_url(self):
        return self.cite_url('ris')

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
