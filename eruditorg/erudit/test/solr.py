from collections import Counter
from itertools import chain
from operator import attrgetter

from luqum.tree import (
    SearchField, Group, AndOperation, OrOperation, UnknownOperation, FieldGroup
)
from luqum.parser import parser

# This fake solr client doesn't try to re-implement solr query parser. It expects a very specific
# list of queries and return results according to its very basic database.


SOLR2DOC = {
    'ID': 'id',
    'AuteurNP_fac': 'authors',
    'Auteur_tri': 'authors',
    'Titre_fr': 'title',
    'Corpus_fac': 'type',
    'TypeArticle_fac': 'article_type',
    'RevueAbr': 'journal_code',
    'AnneePublication': 'year',
    'DateAjoutErudit': 'date_added',
    'Fonds_fac': 'collection',
    'Editeur': 'collection',
}


class SolrDocument:
    def __init__(self, id, title, type, authors, **kwargs):
        self.id = id
        self.title = title
        self.type = type
        self.authors = authors
        OPTIONAL_ARGS = [
            'article_type', 'journal_code', 'collection', 'year', 'date_added', 'repository']
        for attr in OPTIONAL_ARGS:
            val = kwargs.get(attr)
            if isinstance(val, int):
                val = str(val)
            setattr(self, attr, val)

    @staticmethod
    def from_article(article, authors=None):
        if not authors:
            if hasattr(article, 'erudit_object'):
                authors = article.erudit_object.get_authors()
            authors = authors or []
        article_type = article.type
        if article_type == 'compterendu':
            article_type = 'Compte rendu'
        journal = article.issue.journal
        return SolrDocument(
            id=article.localidentifier,
            journal_code=journal.code,
            title=article.title,
            type='Article' if article.issue.journal.is_scientific() else 'Culturel',
            article_type=article_type,
            authors=authors,
            year=str(article.issue.year),
            collection=journal.collection.name)

    def as_result(self):
        result = {}
        for solr, attrname in SOLR2DOC.items():
            val = getattr(self, attrname)
            if val is not None:
                result[solr] = val
        return result


class FakeSolrResults:
    def __init__(self, docs=None, facet_fields=None, rows=None):
        if docs is None:
            docs = []
        if facet_fields is None:
            facet_fields = {}
        self.hits = len(docs)
        if rows:
            docs = list(docs)[:int(rows)]
        self.docs = [d.as_result() for d in docs]
        self.facets = {
            'facet_fields': facet_fields,
        }


def unescape(s):
    if s.startswith('"') and s.endswith('"'):
        s = s[1:-1]
    return s.replace('\\-', '-')


def normalize_pq(pq):
    if isinstance(pq, (Group, FieldGroup)):
        return normalize_pq(pq.children[0])
    elif isinstance(pq, (AndOperation, OrOperation, UnknownOperation)):
        children = map(normalize_pq, pq.children)
        normalised_class = type(pq)
        if isinstance(pq, UnknownOperation):
            normalised_class = AndOperation
        return normalised_class(*children)
    elif isinstance(pq, SearchField):
        return SearchField(pq.name, normalize_pq(pq.children[0]))
    return pq


# example pattern: (SearchField, {'name': 'RevueAbr'}, [])
def matches_pattern(pq, pattern):
    pclass, pattrs, pchildren = pattern
    if not isinstance(pq, pclass):
        return False
    for k, v in pattrs.items():
        if k != 'flags' and getattr(pq, k) != v:
            return False
    if pchildren:
        # Order doesn't matter for children matching
        for c1 in pq.children:
            for c2 in list(pchildren):
                if matches_pattern(c1, c2):
                    pchildren.remove(c2)
                    break
            else:
                return False
        for child in pchildren:
            child_attrs = child[1]
            if 'optional' not in child_attrs.get('flags', set()):
                return False
        return True
    else:
        return True


def extract_pq_searchvals(pq):
    result = {}
    for child in pq.children:
        result.update(extract_pq_searchvals(child))
    if isinstance(pq, SearchField):
        result[pq.name] = unescape(pq.expr.value)
    return result


class FakeSolrClient:
    def __init__(self, *args, **kwargs):
        self.authors = {}
        self.by_id = {}

    def add_document(self, doc):
        for author in doc.authors:
            docs = self.authors.setdefault(author, [])
            docs.append(doc)
        self.by_id[doc.id] = doc

    def add_article(self, article, authors=None):
        self.add_document(SolrDocument.from_article(article, authors=authors))

    def search(self, *args, **kwargs):
        def get_facet(elems):
            try:
                counter = Counter(elems)
            except TypeError:
                # elems are lists
                counter = Counter(chain(*elems))
            result = []
            for k, v in counter.items():
                result += [k, v]
            return result

        def apply_filters(docs, searchvals):
            def val_matches(docval, searchval):
                if searchval.endswith('*'):
                    if docval.startswith(searchval[:-1]):
                        return True
                elif docval == searchval:
                    return True
                return False

            def matches(doc):
                for k, v in searchvals.items():
                    docval = getattr(doc, SOLR2DOC[k])
                    if not isinstance(docval, list):
                        docval = [docval]
                    if not any(val_matches(subval, v) for subval in docval):
                        return False
                return True

            return list(filter(matches, docs))

        def create_results(docs, facets=[]):
            # Add facets
            facet_fields = {}
            for facet in facets:
                facet_fields[facet] = get_facet([getattr(d, SOLR2DOC[facet]) for d in docs])

            # apply sorting
            sort_args = kwargs.get('sort')
            if sort_args:
                if isinstance(sort_args, str):
                    sort_args = [sort_args]
                for sort_arg in reversed(sort_args):
                    field_name, order = sort_arg.split()
                    reverse = order == 'desc'
                    sortattr = SOLR2DOC[field_name]
                    docs = sorted(docs, key=attrgetter(sortattr), reverse=reverse)

            return FakeSolrResults(docs=docs, facet_fields=facet_fields, rows=kwargs.get('rows'))

        q = kwargs.get('q') or args[0]
        fq = kwargs.get('fq')
        if fq:
            q = '{} AND {}'.format(q, fq)
        pq = normalize_pq(parser.parse(q))
        my_pattern = (SearchField, {'name': 'ID'}, [])
        if matches_pattern(pq, my_pattern):
            searchvals = extract_pq_searchvals(pq)
            solr_id = searchvals['ID']
            try:
                return create_results(docs=[self.by_id[solr_id]])
            except KeyError:
                return FakeSolrResults()

        my_pattern1 = (SearchField, {'name': 'RevueAbr'}, [])
        my_pattern2 = (AndOperation, {}, [
            (SearchField, {'name': 'RevueAbr'}, []),
            (SearchField, {'name': 'TypeArticle_fac'}, []),
        ])
        if matches_pattern(pq, my_pattern1) or matches_pattern(pq, my_pattern2):
            # letter list or article types, return facets
            searchvals = extract_pq_searchvals(pq)
            journal_code = searchvals['RevueAbr']
            result = []
            for author, docs in self.authors.items():
                docs = apply_filters(docs, searchvals)
                result += [doc for doc in docs if doc.journal_code == journal_code]
            return create_results(result, facets=['AuteurNP_fac', 'TypeArticle_fac'])

        my_pattern = (AndOperation, {}, [
            (SearchField, {'name': 'RevueAbr'}, []),
            (SearchField, {'name': 'AuteurNP_fac'}, []),
            (SearchField, {'name': 'TypeArticle_fac', 'flags': {'optional'}}, []),
        ])
        if matches_pattern(pq, my_pattern):
            # query for articles with matching author names
            searchvals = extract_pq_searchvals(pq)
            journal_code = searchvals['RevueAbr']
            first_letter = searchvals['AuteurNP_fac'][:1]
            result = []
            for author, docs in self.authors.items():
                if author.startswith(first_letter):
                    docs = apply_filters(docs, searchvals)
                    for doc in docs:
                        result.append(doc)
            return create_results(docs=result)

        my_pattern1 = (SearchField, {'name': 'TexteComplet'}, [])
        my_pattern2 = (AndOperation, {}, [
            (SearchField, {'name': 'TexteComplet'}, []),
            (SearchField, {'name': 'TypeArticle_fac', 'flags': {'optional'}}, []),
        ])
        if matches_pattern(pq, my_pattern1) or matches_pattern(pq, my_pattern2):
            # free-text query. For now, we perform a very simple search on title
            searchvals = extract_pq_searchvals(pq)
            searched_words = set(searchvals['TexteComplet'].lower().split())
            result = []
            docs = self.by_id.values()
            docs = apply_filters(docs, searchvals)
            for doc in docs:
                words = set(doc.title.lower().split())
                if searched_words & words:
                    result.append(doc)
            return create_results(docs=result)

        my_pattern1 = (SearchField, {'name': 'Corpus_fac'}, [])
        my_pattern2 = (AndOperation, {}, [
            (SearchField, {'name': 'Corpus_fac'}, []),
            (SearchField, {'name': 'Editeur'}, []),
            (SearchField, {'name': 'AnneePublication', 'flags': {'optional'}}, []),
            (SearchField, {'name': 'Auteur_tri', 'flags': {'optional'}}, []),
        ])
        if matches_pattern(pq, my_pattern1) or matches_pattern(pq, my_pattern2):
            # Thesis listing
            searchvals = extract_pq_searchvals(pq)
            result = []
            docs = self.by_id.values()
            docs = apply_filters(docs, searchvals)
            return create_results(docs=docs, facets=['AnneePublication', 'AuteurNP_fac'])

        print("Unexpected query {} {}".format(q, repr(pq)))
        return FakeSolrResults()
