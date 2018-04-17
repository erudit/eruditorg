from collections import Counter

from luqum.tree import (
    SearchField, Group, AndOperation, OrOperation, UnknownOperation, FieldGroup
)
from luqum.parser import parser

# This fake solr client doesn't try to re-implement solr query parser. It expects a very specific
# list of queries and return results according to its very basic database.


class FakeSolrResults:
    def __init__(self, docs=None, facet_fields=None):
        if docs is None:
            docs = []
        if facet_fields is None:
            facet_fields = {}
        self.hits = len(docs)
        self.docs = docs
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

    def add_article(self, article, authors=None):
        if not authors:
            if hasattr(article, 'erudit_object'):
                authors = article.erudit_object.get_authors()
            authors = authors or []
        if article.type == 'compterendu':
            article_type = 'Compte rendu'
        else:
            article_type = 'Article' if article.issue.journal.is_scientific() else 'Culturel'
        article_dict = {
            'id': article.localidentifier,
            'journal_code': article.issue.journal.code,
            'title': article.title,
            'type': article_type,
            'authors': authors,
        }
        for author in authors:
            articles = self.authors.setdefault(author, [])
            articles.append(article_dict)
        self.by_id[article_dict['id']] = article_dict

    def add_thesis(self, thesis):
        thesis_dict = {
            'id': thesis.localidentifier,
            'title': thesis.title,
            'type': 'Thèses',
            'authors': [str(thesis.author)],
        }
        self.by_id[thesis_dict['id']] = thesis_dict

    def search(self, *args, **kwargs):
        def single_result(article):
            result = {
                'ID': article['id'],
                'AuteurNP_fac': article['authors'],
                'Titre_fr': article['title'],
                'Corpus_fac': article['type'],
            }
            if 'journal_code' in article:
                result['RevueAbr'] = article['journal_code']
            return result

        def get_facet(elems):
            counter = Counter(elems)
            result = []
            for k, v in counter.items():
                result += [k, v]
            return result

        q = kwargs.get('q') or args[0]
        pq = normalize_pq(parser.parse(q))
        print(q, repr(pq))
        my_pattern = (SearchField, {'name': 'ID'}, [])
        if matches_pattern(pq, my_pattern):
            searchvals = extract_pq_searchvals(pq)
            solr_id = searchvals['ID']
            try:
                return FakeSolrResults(docs=[single_result(self.by_id[solr_id])])
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
            filter_by_type = searchvals.get('TypeArticle_fac')
            authors = []
            article_types = []
            for author, articles in self.authors.items():
                for article in articles:
                    if filter_by_type and article['type'] != filter_by_type:
                        continue
                    if article['journal_code'] == journal_code:
                        authors.append(author)
                        article_types.append(article['type'])
            return FakeSolrResults(facet_fields={
                'AuteurNP_fac': get_facet(authors),
                'TypeArticle_fac': get_facet(article_types),
            })

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
            filter_by_type = searchvals.get('TypeArticle_fac')
            result = []
            for author, articles in self.authors.items():
                if author.startswith(first_letter):
                    for article in articles:
                        if filter_by_type and article['type'] != filter_by_type:
                            continue
                        result.append(single_result(article))
            return FakeSolrResults(docs=result)

        print("Unexpected query {} {}".format(q, repr(pq)))
        return FakeSolrResults()
