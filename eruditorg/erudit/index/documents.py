# -*- coding: utf-8 -*-

import itertools

from .conf import settings as index_settings


def get_bulk_operation_metadata(erudit_document):
    """ Returns the bulk operation metadata associated wit the considered Érudit document. """
    return {
        'index': {
            '_index': index_settings.ES_INDEX_NAME,
            '_type': index_settings.ES_INDEX_DOC_TYPE,
            '_id': erudit_document.localidentifier,
        }
    }


def get_article_document_from_fedora(article):
    """ Returns a dictionary corresponding to the given article by using Fedora. """
    issue = article.issue
    journal = issue.journal

    authors = [
        '{0} {1}'.format(a['lastname'], a['firstname']) for a in article.erudit_object.authors]
    author_affiliations = list(itertools.chain.from_iterable([
        a.get('affiliations', []) for a in article.erudit_object.authors]))
    keywords = list(itertools.chain.from_iterable(
        [kd.get('keywords', []) for kd in article.erudit_object.keywords]))
    abstracts = [ad.get('content') for ad in article.erudit_object.abstracts]
    text = article.erudit_object.stringify_children(article.erudit_object.find('corps'))
    refbiblios = [
        article.erudit_object.stringify_children(n)
        for n in article.erudit_object.findall('refbiblio')]

    _doc = {
        'localidentifier': article.localidentifier,
        'publication_date': issue.erudit_object.publication_date,
        'publication_year': issue.erudit_object.publication_year,
        'number': issue.erudit_object.number,
        'issn': article.erudit_object.issn,
        'issn_num': article.erudit_object.issn_num,
        'isbn': article.erudit_object.isbn,
        'isbn_num': article.erudit_object.isbn_num,
        'authors': authors,
        'author_affiliations': author_affiliations,
        'keywords': keywords,
        'abstracts': abstracts,
        'title': article.erudit_object.title,
        'subtitle': article.erudit_object.subtitle,
        'text': text,
        'refbiblios': refbiblios,
        'article_type': article.erudit_object.article_type,
        'lang': article.erudit_object.lang,
        'collection': journal.name,
    }
    return {k: v if v is not None else '' for k, v in _doc.items()}
