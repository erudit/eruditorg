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

    authors = [
        '{0} {1}'.format(a['firstname'], a['lastname']) for a in article.erudit_object.authors]
    keywords = list(itertools.chain.from_iterable(
        [kd.get('keywords', []) for kd in article.erudit_object.keywords]))
    abstracts = [ad.get('content') for ad in article.erudit_object.abstracts]
    text = article.erudit_object.stringify_children(article.erudit_object.find('corps'))

    return {
        'localidentifier': article.localidentifier,
        'publication_year': issue.erudit_object.publication_year,
        'number': issue.erudit_object.number,
        'issn': article.erudit_object.issn,
        'authors': authors,
        'keywords': keywords,
        'abstracts': abstracts,
        'title': article.erudit_object.title,
        'subtitle': article.erudit_object.subtitle,
        'text': text,

        # 'isbn': ???,
    }
