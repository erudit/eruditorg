import re


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
        def get_filter_by_type(q):
            m = re.match(r'^.*TypeArticle_fac:"(.+)"$', q)
            if m:
                return m.group(1)
            else:
                return None

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

        q = kwargs.get('q') or args[0]
        m = re.match(r'^RevueAbr:([\w\-]+) AuteurNP_fac:\((\w)\*\).*$', q)
        if m:
            # query for articles with matching author names
            journal_code = m.group(1)
            first_letter = m.group(2)
            filter_by_type = get_filter_by_type(q)
            result = []
            for author, articles in self.authors.items():
                if author.startswith(first_letter):
                    for article in articles:
                        if filter_by_type and article['type'] != filter_by_type:
                            continue
                        result.append(single_result(article))
            return FakeSolrResults(docs=result)
        m = re.match(r'^RevueAbr:([\w\-]+).*$', q)
        if m:
            # letter list, return facets
            journal_code = m.group(1)
            filter_by_type = get_filter_by_type(q)
            authors = []
            for author, articles in self.authors.items():
                for article in articles:
                    if filter_by_type and article['type'] != filter_by_type:
                        continue
                    if article['journal_code'] == journal_code:
                        authors += [author, 42]
                        break
            return FakeSolrResults(facet_fields={'AuteurNP_fac': authors})

        m = re.match(r'^ID:"(.+)"$', q)
        if m:
            solr_id = m.group(1)
            try:
                return FakeSolrResults(docs=[single_result(self.by_id[solr_id])])
            except KeyError:
                return FakeSolrResults()

        print("Unexpected query {}".format(q))
        return FakeSolrResults()
