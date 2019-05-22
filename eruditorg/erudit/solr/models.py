from django.conf import settings
from django.urls import reverse
from django.utils.translation import ugettext as _
import pysolr

from core.solrq.query import solr_escape
from erudit import models as erudit_models
from erudit.templatetags.model_formatters import person_list

# This is the object that will be used to query the Solr index.
client = pysolr.Solr(settings.SOLR_ROOT, timeout=settings.SOLR_TIMEOUT)


class SolrDocument:
    def __init__(self, solr_data):
        self.localidentifier = solr_data['ID']
        self.corpus = solr_data.get('Corpus_fac')
        self.solr_data = solr_data

    @staticmethod
    def from_solr_id(solr_id):
        solr_data = get_solr_data_from_id(solr_id)
        return get_model_instance(solr_data)

    def can_cite(self):
        return False

    @property
    def document_type(self):
        return {
            'Dépot': 'report',
            'Livres': 'book',
            'Actes': 'book',
            'Rapport': 'report',
            'Article': 'article',
            'Culturel': 'article',
            'Thèses': 'thesis',
        }.get(self.corpus, 'generic')

    @property
    def year(self):
        return self.solr_data['Annee'][0] if 'Annee' in self.solr_data else None

    @property
    def publication_year(self):
        return self.solr_data.get('AnneePublication')

    @property
    def issn(self):
        return self.solr_data.get('ISSN')

    @property
    def collection_display(self):
        return self.solr_data.get('Fonds_fac')

    @property
    def authors_list(self):
        return self.solr_data.get('AuteurNP_fac', [])

    @property
    def authors_display(self):
        return person_list(self.authors_list)

    @property
    def volume(self):
        return self.solr_data.get('Volume')

    @property
    def series_display(self):
        collection_title = self.solr_data.get('TitreCollection_fac')
        if collection_title:
            return collection_title[0]
        else:
            return None

    @property
    def urls(self):
        return self.solr_data['URLDocument'] if 'URLDocument' in self.solr_data else []

    @property
    def url(self):
        urls = self.urls
        return urls[0] if urls else None

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
        TITLE_ATTRS = [
            'Titre_fr', 'Titre_en', 'Titre_defaut', 'TitreRefBiblio_aff']
        for attrname in TITLE_ATTRS:
            if attrname in self.solr_data:
                return self.solr_data[attrname]
        return _("(Sans titre)")


class Article(SolrDocument):
    @property
    def article_type(self):
        if 'TypeArticle_fac' not in self.solr_data:
            return 'article'
        article_type = self.solr_data['TypeArticle_fac']
        return {
            'Compterendu': 'compterendu',
            'Compte rendu': 'compterendu',
            'Autre': 'autre',
            'Note': 'note',
        }.get(article_type, 'article')

    @property
    def type_display(self):
        article_type = self.article_type
        return erudit_models.Article.TYPE_DISPLAY.get(article_type, article_type)

    @property
    def journal_type(self):
        return 'S'


class Thesis(SolrDocument):
    def can_cite(self):
        return True

    def cite_url(self, type):
        return reverse('public:thesis:thesis_citation_{}'.format(type), args=[
            self.localidentifier,
        ])

    def cite_enw_url(self):
        return self.cite_url('enw')

    def cite_bib_url(self):
        return self.cite_url('bib')

    def cite_ris_url(self):
        return self.cite_url('ris')

    @property
    def collection_display(self):
        result = self.solr_data.get('Editeur')
        if isinstance(result, list):
            return result[0] if result else ''
        else:
            return result

    @property
    def abstract(self):
        return self.solr_data.get('Resume_fr')


def get_model_instance(solr_data):
    generic = SolrDocument(solr_data)
    if generic.document_type == 'thesis':
        return Thesis(solr_data)
    elif generic.document_type == 'article':
        try:
            return erudit_models.Article.from_solr_object(Article(solr_data))
        except erudit_models.Article.DoesNotExist:
            # The only case where this can happen is if we don't have a parent Issue. Otherwise,
            # even when erudit_models.Article referes to an article that isn't in fedora, it's
            # supposed to do fine.
            return Article(solr_data)
    else:
        return SolrDocument(solr_data)


def get_fedora_ids(localidentifier):
    query = 'ID:{}'.format(localidentifier)
    args = {
        'q': query,
        'facet.limit': '0',
        'fl': 'ID,NumeroID,RevueID',
    }
    solr_results = client.search(**args)
    if solr_results.hits:
        doc = solr_results.docs[0]
        return (doc['RevueID'], doc['NumeroID'], doc['ID'])
    else:
        return None


def get_all_articles(rows, page):
    query = 'Fonds_fac:Érudit Corpus_fac:Article'
    args = {
        'q': query,
        'facet.limit': '0',
        'rows': str(rows),
        'start': str((page - 1) * rows),
    }
    solr_results = client.search(**args)

    def get(solr_data):
        solr_doc = SolrDocument(solr_data)
        if solr_doc.document_type != 'article':
            return None
        try:
            return erudit_models.Article.from_solr_object(Article(solr_data))
        except erudit_models.Article.DoesNotExist:
            print("Warning: Article {} from Solr does not exist in Fedora!".format(solr_data['ID']))
            return None

    result = (get(d) for d in solr_results.docs)
    return [a for a in result if a is not None]


def get_total_number_of_articles():
    query = 'Fonds_fac:Érudit Corpus_fac:Article'
    return client.search(query).hits


def get_solr_data_from_id(solr_id):
    results = client.search(q='ID:"{}"'.format(solr_escape(solr_id)))
    if not results.hits:
        raise ValueError("No Solr object found")
    elif results.hits > 1:
        raise ValueError("Multiple Solr objects found")
    return results.docs[0]
