from django.utils.translation import ugettext as _

from erudit.templatetags.model_formatters import person_list


def serialize_solr_result(result):
    corpus = result['Corpus_fac']
    document_type = {
        'Article': 'article',
        'Culturel': 'article',
        'Thèses': 'thesis',
        'Dépot': 'report',
        'Livres': 'book',
        'Actes': 'book',
        'Rapport': 'report',
    }.get(corpus, 'generic')
    collection_title = result.get('TitreCollection_fac')
    if collection_title:
        series = collection_title[0]
    else:
        series = None
    if not {'PremierePage', 'DernierePage'}.issubset(set(result.keys())):
        pages = None
    else:
        pages = _('Pages {firstpage}-{lastpage}'.format(
            firstpage=result['PremierePage'],
            lastpage=result['DernierePage']
        ))
    TITLE_ATTRS = ['Titre_fr', 'Titre_en', 'TitreRefBiblio_aff']
    title = _("(Sans titre)")
    for attrname in TITLE_ATTRS:
        if attrname in result:
            title = result[attrname]
            break
    return {
        'localidentifier': result['ID'],
        'document_type': document_type,
        'year': result['Annee'][0] if 'Annee' in result else None,
        'publication_date': result.get('AnneePublication'),
        'issn': result.get('ISSN'),
        'collection': result.get('Fonds_fac'),
        'authors': person_list(result.get('AuteurNP_fac')),
        'volume': result.get('Volume'),
        'series': series,
        'url': result['URLDocument'][0] if 'URLDocument' in result else None,
        'numero': result.get('Numero'),
        'pages': pages,
        'title': title,
    }


class GenericSolrDocumentSerializer:
    def __init__(self, objs, **kwargs):
        self.objs = objs

    @property
    def data(self):
        return map(serialize_solr_result, self.objs)
